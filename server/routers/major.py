from djadmin.eecs.models import Major, Point1, Point2
from pydantic import BaseModel, Field
from typing import List, Any
from server.auth.login import manager as login_manager
from fastapi import Depends, APIRouter, HTTPException
from .schema import *

router = APIRouter()


@router.get('/majors', response_model=ListData)
def getMajors(user=Depends(login_manager)):
    """
    获取user负责的所有专业
    """
    major_list = list(Major.objects.filter(manager=user).values('id', 'name'))
    major_list_len = len(major_list)
    return {
        "code": 20000,
        "data": {
            "total": major_list_len,
            "items": major_list
        }
    }


@router.get('/point1', response_model=ListData)
def getPoint1(major_id: int, user=Depends(login_manager)):
    """
    获取专业编号=major_id的毕业要求
    :return:
    """
    major = Major.objects.get(id=major_id, manager=user)
    point1_list = list(Point1.objects.filter(major=major).values('id', 'name', 'index'))
    return {
        "code": 20000,
        "data": {
            "total": len(point1_list),
            "items": point1_list
        }
    }


@router.post('/point1/create')
def createPoint1(major_id: int, index: int, content: str, user=Depends(login_manager)):
    """
    创建 content = content, index = index的毕业要求, index不能与已有指标点重复,
    code=20000 创建成功
    code=40001 创建失败
    """
    major = Major.objects.get(id=major_id)
    # 检查user是否未本专业的负责人
    if major.manager != user:
        raise HTTPException(status_code=401)
    # 如果已经存在index，则返回40001错误
    if Point1.objects.filter(major=major, index=index).count() > 0:
        return {"code": 40001, "detail": "该专业此序号已存在"}
    else:
        Point1.objects.create(major=major, index=index, content=content)
        return {
            "code": 20000,
            "detail": "创建成功"
        }


@router.post('/point1/update/content')
def updatePoint1Content(point1_id: int, content: str, user=Depends(login_manager)):
    """
    修改id = point1_id的毕业要求的content为content
    code=20000 修改成功
    code=40001 修改失败
    """
    point1 = Point1.objects.get(point1_id=point1_id)
    # 检查user是否为本专业的负责人
    if point1.major.manager != user:
        raise HTTPException(status_code=401)
    else:
        point1.content = content
        point1.save()
        return {
            "code": 20000,
            "detail": "修改成功"
        }


@router.post('/point1/delete')
def deletePoint1(point1_id: int, user=Depends(login_manager)):
    """
    删除id = point1_id的毕业要求
    code=20000 删除成功
    code=40001 删除失败
    """
    point1 = Point1.objects.get(id=point1_id)
    # 检查user是否为point1对应的专业的专业负责人
    if point1.major.manager != user:
        raise HTTPException(status_code=401)
    point1.delete()
    return {
        "code": 20000,
        "detail": "删除成功"
    }


@router.get("/point2", response_model=ListData)
def getPoint2(point1_id: int, user=Depends(login_manager)):
    """
    获取id = point1_id的分解指标点
    """
    point1 = Point1.objects.get(id=point1_id)
    # 检测权限
    if point1.major.manager != user:
        raise HTTPException(status_code=404, detail="未查询到毕业要求")
    point2_list = list(Point2.objects.filter(point1=point1).values('id', 'index', 'name'))
    return {
        "code": 20000,
        "data": {
            "total": len(point2_list),
            "items": point2_list
        }
    }


@router.post('/point2/create')
def createPoint2(point1_id: int, index: int, content: str, user=Depends(login_manager)):
    """
    创建content = content, index = index的毕业要求,index不能与已有指标点重复,
    code=20000 创建成功
    code=40001 创建失败
    """
    point1 = Major.objects.get(id=point1_id)
    # 检查user是否为对应的一级指标点对应的专业的专业负责人
    if point1.major.manager != user:
        raise HTTPException(status_code=401)
    # 如果已经存在index，则返回40001错误
    if Point2.objects.filter(point1=point1, index=index).count() > 0:
        return {"code": 40001, "detail": "该专业此序号已存在"}
    else:
        Point2.objects.create(point1=point1, index=index, content=content)
        return {
            "code": 20000,
            "detail": "创建成功"
        }


@router.post('/point2/delete')
def deletePoint2(point2_id: int, user=Depends(login_manager)):
    """
    删除id = point2_id的分解指标点
    code=20000 删除成功, code=40001 删除失败
    """
    point2 = Point2.objects.get(id=point2_id)
    # 检查user是否为point1对应的专业的专业负责人
    if point2.point1.major.manager != user:
        raise HTTPException(status_code=401)
    point2.delete()
    return {
        "code": 20000,
        "detail": "删除成功"
    }


@router.post('/point2/update/content')
def updatePoint2Content(point2_id: int, content: str, user=Depends(login_manager)):
    """
    修改id = point2_id的分解指标点的content为content
    code=20000 修改成功
    code=40001 修改失败
    """
    point2 = Point1.objects.get(point1_id=point2_id)
    # 检查user是否为本专业的负责人
    if point2.point1.major.manager != user:
        raise HTTPException(status_code=401)
    else:
        point2.content = content
        point2.save()
        return {
            "code": 20000,
            "detail": "修改成功"
        }