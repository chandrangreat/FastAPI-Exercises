import json

from fastapi import FastAPI, status

from fastapi.responses import JSONResponse, Response

from typing import Union

from bson import json_util

from bson.objectid import ObjectId

from pydantic import BaseModel

import pprint

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client.libraryManagement

app = FastAPI()

class Student(BaseModel):
    name: str
    email: str
    grade: int

#  Get All Students
@app.get("/student")
async def get_students():
    students = []
    cursor = db.students.find({}).sort('i')
    for document in await cursor.to_list(length=100):
        pprint.pprint(document)
        students.append(document)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(json_util.dumps(students)))

# Get student By Id
@app.get("/student/{id}")
async def get_studentById(id: str):
    print("CRACK", type(id),ObjectId(id))
    student = await db.students.find_one({"_id": ObjectId(id)})
    print("BELLOW",student)
    pprint.pprint(student)
    return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(json_util.dumps(student)))

# Create a new student
@app.post("/student")
async def write_student(student_object: Student):
    document = student_object.model_dump()
    result = await db.students.insert_one(document)
    created_student = await db.students.find_one({"_id": result.inserted_id})
    print('result %s' % repr(created_student))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=json.loads(json_util.dumps(created_student)))

# Edit student data
@app.put("/student/{id}")
async def edit_student(id: str, student_object: Student):
    document = student_object.model_dump()
    await db.students.replace_one({'_id': ObjectId(id)}, document)
    updated_student = await db.students.find_one({'_id': ObjectId(id)})
    return JSONResponse(status_code=status.HTTP_200_OK, content=json.loads(json_util.dumps(updated_student)))

# Delete Student
@app.delete("/student/{id}")
async def delete_student(id: str):
    deleted_object = await db.students.delete_one({'_id': ObjectId(id)})
    pprint.pprint(deleted_object)
    deleted_count = deleted_object.deleted_count
    if deleted_count > 0:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)