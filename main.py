from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from typing import Annotated
import sqlite3

con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

app = FastAPI()

#글쓰기 내용 저장
@app.post('/items')
async def create_item(image:UploadFile, 
                title:Annotated[str,Form()],
                price:Annotated[int,Form()],
                description:Annotated[str,Form()],
                place:Annotated[str,Form()],
                insertAt:Annotated[int,Form()]):
    image_bytes = await image.read()
    #sql문 실행
    cur.execute(f"""
                INSERT INTO items(title, image, price, description, place, insertAt)
                VALUES ('{title}','{image_bytes.hex()}','{price}','{description}','{place}','{insertAt}')
                """)
    #데이터 삽입
    con.commit()
    return '200'    

@app.get('/items')
async def get_items():
    #데이터 뿐만 아니라 컬럼명도 앞에 붙어서 저장됨
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items;
                       """).fetchall()
    return JSONResponse(jsonable_encoder(dict(rows) for rows in rows))

@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes))

#하위 > 상위 경로로 순차적으로 작성해야 한다. 상위 경로가 먼저 작성되면 모든 요청을 상위 경로것으로 가져오게 된다.
app.mount("/",StaticFiles(directory="frontend",html=True),name="frontend")
