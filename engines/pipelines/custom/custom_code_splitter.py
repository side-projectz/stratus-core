import uuid
from tqdm import tqdm
from typing import List
from pydantic import BaseModel
from llama_index.core import Document
from llama_index.core.schema import TransformComponent
from llama_index.core.program import LLMTextCompletionProgram

from .pydantic_output_parser.json_repair import JSONRepairPydanticOutputParser


class PageChunk(BaseModel):
    start: int
    end: int


class PageSplitter(BaseModel):
    split: bool  # Indicates whether the document should be chunked
    chunks: List[PageChunk] | None  # If `split` is False, this will be None


class CustomCodeSplitter(TransformComponent):

    def __call__(self, nodes: List[Document], **kwargs) -> List[Document]:
        """
        Splits code documents into chunks based on logical structures using LLM assistance.

        Args:
            nodes (List[Document]): List of documents to process.
            **kwargs: Additional arguments.

        Returns:
            List[Document]: List of processed documents with optional splitting applied.
        """
        print(len(nodes))
        updated_documents = []

        with tqdm(
            total=len(nodes), desc="Processing Documents", unit="document"
        ) as progress_bar:

            for original_node in nodes:
                # Add line numbers to the document for processing
                document_with_lines = self._add_line_numbers(original_node)

                # Initialize the LLM program with the prompt and expected output format
                parser = JSONRepairPydanticOutputParser(output_cls=PageSplitter)
                program = LLMTextCompletionProgram.from_defaults(
                    output_parser=parser,
                    output_cls=PageSplitter,
                    prompt_template_str=CUSTOM_UNIVERSAL_SPLITTER_PROMPT_TEMPLATE,
                    verbose=True,
                )

                # Generate chunking decisions from the LLM
                chunking_result: PageSplitter = program(
                    document=document_with_lines.text
                )

                # If no splitting is required, keep the original document
                if not chunking_result.split:
                    updated_documents.append(original_node)
                    progress_bar.update(1)
                    continue

                # Generate new documents based on the chunks
                chunked_documents = self._create_chunks(original_node, chunking_result)
                updated_documents.extend(chunked_documents)
                progress_bar.update(1)

        print(len(updated_documents))
        return updated_documents

    def _add_line_numbers(self, document: Document) -> Document:
        """
        Adds line numbers to the document's text for better LLM interpretation.

        Args:
            document (Document): Original document.

        Returns:
            Document: Document with line numbers prepended to each line.
        """
        lines = document.text.splitlines()
        doc_meta = f"""
File MetaData
file_name: {document.metadata['file_name']}
file_path: {document.metadata['file_path']}
"""
        numbered_lines = [f"[line:{idx + 1}] {line}" for idx, line in enumerate(lines)]
        updated_text = f"{doc_meta}\n" + "\n".join(numbered_lines)
        # document.set_content(updated_text)

        new_document = Document(doc_id=str(uuid.uuid4()), metadata=document.metadata)
        new_document.set_content(updated_text)
        return new_document

    def _create_chunks(
        self,
        original_document: Document,
        chunking_result: PageSplitter,
    ) -> List[Document]:
        """
        Creates new document chunks based on the chunking result.

        Args:
            original_document (Document): Original document to split.
            chunking_result (PageSplitter): The chunking decision from the LLM.

        Returns:
            List[Document]: List of chunked documents.
        """
        chunks = []
        lines = original_document.text.splitlines()

        for _idx, chunk in enumerate(chunking_result.chunks):
            # Extract the lines corresponding to the chunk
            chunk_lines = lines[chunk.start : chunk.end]
            chunk_text = "\n".join(chunk_lines).strip()

            # Skip empty or whitespace-only chunks
            if not chunk_text:
                continue

            # Create a new document for the chunk
            new_document = Document(
                doc_id=str(uuid.uuid4()), metadata=original_document.metadata
            )

            new_document.metadata["chunk"] = f"chunk_{_idx+1}"
            new_document.set_content(chunk_text)
            chunks.append(new_document)

        return chunks


CUSTOM_UNIVERSAL_SPLITTER_PROMPT_TEMPLATE = """
You are a Page Splitter system that takes a single document and decides how to chunk it for RAG-based indexing.
Produce a JSON object describing how to split the document into meaningful chunks, following the rules below.

## Output Format
You must produce a JSON object in the following format:

{
    "split": <bool>,
    "chunks": <list | null>
}

where:
- "split" is `true` if chunking is needed, or `false` if the document is too short or does not warrant splitting.
- "chunks" is a list of PageChunk objects if "split" is true; otherwise, it is `null`.

### PageChunk Object
Each element in the "chunks" list is a JSON object of the form:

{
    "start": <int>,
    "end": <int>
}

- "start" and "end" refer to line numbers within the document (1-based).

## Chunking Rules

1. **Relevance Check**  
   - First, determine if the document contains user-relevant or human-readable information. 
     If it is predominantly auto-generated (e.g., large machine-generated files) or 
     not typically reviewed by a human, you may set `"split": false` and `"chunks": null`.

2. **Logical Units**  
    - Identify cohesive sections or semantic units, such as:
      • For code: functions, classes, or closely related statements.
      • For Markdown or text: paragraphs, headings with their content, or bullet lists.
      • For config files or .gitignore: related blocks of settings or rules.
    - Each chunk should represent a complete thought or unit.

3. **Preserve Context**  
    - Avoid splitting in the middle of a cohesive section (e.g., half a function or half a paragraph).

4. **Size Constraints**  
    - Aim for chunks in the range of 10–50 lines. If a single logical unit exceeds 50 lines, split it at 
      a sub-boundary (e.g., separate methods, subheadings, or paragraph breaks).
    - If the entire document is **within 50–60 lines**, skip chunking (set `"split": false`). Only chunk if the 
      document **exceeds** that limit and warrants logical splitting.

5. **General Structure**  
    - For code files: group related imports at the top in one chunk if they stand alone, or combine them 
      if they are short. 
    - For text/markdown: keep headings with their related paragraphs. 
    - For config files: group lines that share a purpose (e.g., environment settings, ignore rules).
    - Group adjacent lines that are thematically or structurally related (e.g., all imports, all bullet points).

6. **Decision to Chunk**  
    - If the document has fewer than 10 lines, set "split" to `false` and "chunks" to `null`.
    - If the document length is between 10 lines and up to 50–60 lines, also set `"split": false` and `"chunks": null`.
    - Only if the document is relevant and exceeds ~60 lines, apply the rules above to form chunks.

## Additional Requirements

- Every file starts with some reference to `file_name` and `file_path`. You may consider this metadata to determine 
  if the file appears auto-generated (like certain lock, TOML, or YAML files). If you conclude the file is not 
  typically reviewed by users, set `"split": false` and `"chunks": null`.
- Provide enough context in each chunk to keep it semantically self-contained.

## Checklist Before Chunking
1. **Total Line Count**: 
   - If under 10 lines, do not chunk.
   - If 10–60 lines, do not chunk (unless there’s a strong reason to).
   - If over 60 lines, consider chunking.
2. **Auto-Generated Check**:
   - Inspect the file metadata or content to see if it’s likely auto-generated. If so, do not chunk.
3. **Relevance**:
   - If the file is human-readable and relevant, proceed to chunk only if it exceeds 60 lines.
4. **Logical Boundaries**:
   - For relevant documents, respect function, class, paragraph, or heading boundaries.

## Example Output
If chunking is needed:
{
    "split": true,
    "chunks": [
        {
            "start": 1,
            "end": 5
        },
        {
            "start": 6,
            "end": 25
        },
        {
            "start": 26,
            "end": 40
        }
    ]
}

If no chunking is needed (short or irrelevant file):
{
    "split": false,
    "chunks": null
}

## Important Notes
- Use 1-based line numbering (line 1 is the first line).
- Do not include any keys beyond "split" and "chunks".
- Strictly follow the checklist and chunking rules to decide whether to split.

Document:
{document}
"""
