
## 目的

```text
分离出项目中的SQL语句，避免insert/update/delete的SQL语句的重复编写，使用jinja2模板语法实现动态SQL，加入常见的分页、事务、多数据库操作
```

## 注意点

```
1. sql文件夹位置需要根据具体情况修改
2. sql_loader导入需要根据具体项目目录来正确导入
```

![code](https://user-images.githubusercontent.com/30903265/225914280-d7ea7c77-47cf-4169-9dc3-8829c6e23af3.png)


![code1](https://user-images.githubusercontent.com/30903265/225914308-d77e28a9-0675-4bec-83f7-4794cab50012.png)

## 配置事务

![code2](https://user-images.githubusercontent.com/30903265/225914444-6645fc00-4896-45d2-af0f-ad91062d588e.png)

## 项目启动时配置数据库连接对象

![code4](https://user-images.githubusercontent.com/30903265/225914605-884d9ef1-1d49-4c30-877d-1213676cbd15.png)

## 常见操作

#### 增

![code5](https://user-images.githubusercontent.com/30903265/225914763-c622b1a9-2f4a-4140-9d96-17089f1f7264.png)

#### 删

- 物理删除

![code6](https://user-images.githubusercontent.com/30903265/225914843-26ca1e70-7474-4db5-a066-d454b228978f.png)

- 逻辑删除

![code113png](https://user-images.githubusercontent.com/30903265/225915023-5754e83d-2ec7-4d44-b486-13956bd990bd.png)

#### 改

![code7](https://user-images.githubusercontent.com/30903265/225915092-bb702fde-85bc-4e09-99d2-3c53a796caec.png)

#### 使用事务

```python
with db.trans():
  pass
```

或者手动回滚

```python
try:
  ...
except:
  DataBaseHelper.rollback()
else:
  DataBaseHelper.commit()
```

#### option参数与jinja模板语法实现动态SQL

![code8](https://user-images.githubusercontent.com/30903265/225915711-f2fd7942-e1f3-452e-ac2d-46ce8872a826.png)

![code9](https://user-images.githubusercontent.com/30903265/225915732-16b8b995-92e2-4146-9d38-ed30afc176e1.png)

#### 分页(默认使用pageNum与pageSize)

![code10](https://user-images.githubusercontent.com/30903265/225915894-700e900b-6701-415a-9a24-8534ef583134.png)

![code11](https://user-images.githubusercontent.com/30903265/225915934-09314a7d-8174-4563-80c7-c30583f4bfe4.png)

#### 实现多数据库

> 配置

![code15](https://user-images.githubusercontent.com/30903265/225916066-ff1c98ae-cdf4-477e-9a65-46807ca0f4d9.png)

> 使用

![code14](https://user-images.githubusercontent.com/30903265/225916162-458771d0-7237-4b34-915b-15734c741bcd.png)


