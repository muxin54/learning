from fastapi import Query



# class TodoFilter:
#     def __init__(self,done:bool=None):
#         self.done=done

#     async def __call__(self)->dict:
#         return {"done":self.done}

# def todo_filter(done: bool = None):
#     async def _filter():
#         return {"done": done}
#     return _filter

async def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size,}
    


        