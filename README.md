# TakeTheCourse_GDUT
<<<<<<< HEAD
# GDUT教务系统选课助手

# 功能

* 支持自动验证码识别登录。
* 支持关键字、优先级、多备用课程的选课方式。
* 支持批量登录、选课、验证操作。
* 支持批量导入用户。

# 更新说明

* **2019/03/25**
    * 重构核心代码。
    * 支持GUI界面交互。
* **2018/12/20**
    * 上传杂乱代码。


# 使用方法

## **文件 ``Template.xlsx`` 使用方法**

* ``account``  : 教务系统账号
* ``password`` : 教务系统密码
* ``key``      : 所选课程名字（或教师名字）关键字。``,``（英文逗号）: 顺序优先级的与操作 ； ``|`` ：顺序优先级的或操作
  
注意：优先级从左到右



# 说明 
### 由于选课的测试次数限制，所以程序难免会出现选课不成功的问题。
### 建议使用快捷键F4手动选课，而不是依赖自动流程。



=======
# 广东工业大学教务系统自动选课助手

### 该程序主要使用于广东工业大学教务系统（非正方教务系统）的体育抢课选课。


# 功能

  1. 支持自动验证码识别登录。
  2. 支持批量登录选课。
  3. 自动爬取网上免费IP代理，进行IP限制后的继续选课方案。
  4. 支持关键字、优先级、多备用课程的选课方式。
  5. 自动验证选课结果。
 

  
# 使用方法

  **文件 ``userdata.xlsx``里面存放着需要抢课的用户账号密码。（每一行对应一个用户）**
  1. ``account``  : 教务系统账号
  2. ``password`` : 教务系统密码
  3. ``key``      : 所选课程名字（或教师名字）关键字。``,``（英文逗号）: 顺序优先级的与操作 ； ``|`` ：顺序优先级的或操作
  
## 使用案例
* 可选课程：
* ------------------------
* ``体育(4)[羽毛球] 李四 ``
* ``体育(4)[羽毛球] 王五 ``
* ``体育(4)[乒乓球] 赵六 ``
* ``体育(4)[足球] 孙七 ``
* ------------------------
* 张三教务系统账号： 1234567891
* 张三教务系统密码： 123456
* 张三想优先选 王五的羽毛球，如果王五的羽毛球已选满，那么就选足球。
* -----------------------
### 如上情况，那么文件``userdata.xlsx应如下填写。
#### account: 1234567891
#### password: 123456
#### key: 羽毛球,王五|足球


# 说明
  
  程序能完全实现自动选课，但是由于可能存在被忽略的流程问题，所以有兴趣的小伙伴可以自行更改流程代码。
#### 成员登录流程代码处于文件``PoolOp.py``的class ``MemberOp``。
#### 选课流程代码处于文件``TakeCourse.py``的class ``TakeCourse``。
>>>>>>> origin/master

# 该项目仅用于技术交流学习，请不要用于非法用途。

# LICENSE
  Apache-2.0
