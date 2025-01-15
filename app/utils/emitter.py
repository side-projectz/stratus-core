from pyventus import AsyncIOEventEmitter, EventEmitter

event_emitter: EventEmitter = AsyncIOEventEmitter()


__all__ = ["event_emitter"]
