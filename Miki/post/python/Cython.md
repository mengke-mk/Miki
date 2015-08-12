title: 如何使用Cython
date: 2015/08/07
shortcut: use-Cython
categories: Python
tags: Cython, python, C
---

如果需要对python代码添加C/C++的代码,我认为最优先考虑使用的应当是[Cython](http://cython.org/),当然也有其他的方法,比如[这篇文章所说](http://segmentfault.com/a/1190000000479951#articleHeader11).Cython除了能调用原生的C/C++模块外,还可以让你以python的语法来写C/C++的扩展.不过这当中有不少的Tips和Tricks值得注意.

{{ alert('本文中python==2.7.10, Cython=0.22.1', type='info') }}   

## Cython怎么工作?
首先,[Python-C-API](https://docs.python.org/2/c-api/)是Python解释器中原生的python模块,通过这个API就可以使用C/C++来编写Python扩展.不过为了使Python成功的调用C/C++模块,你得花大量的时间写低级的控制,来包裹原来的代码.而Cython所做的就是通过编译利用Python-C-API帮你完成了这个工作,并最终把它编进一个共享库文件(.so)中.使得你可以在python代码中通过`import`直接导入进来.  

一般来讲,在python中使用C/C++模块两种常见的场景是:
- 原来的python代码性能太差
- 有现成的C/C++可供直接调用

首先,你至少得写一个.pyx的文件,写好外部调用的接口函数,然后一个setup.py文件,顺利的话,会生成一个共享库文件(.so),就可以在python代码中`import`它了.  
比如说,如果你要写一个add(x,y)函数,首先:
```python
# add.pyx
def add(x, y):
    return x + y
```
然后一个编译文件:
```python
# setup.py
from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'add',
  ext_modules = cythonize("add.pyx"),
)
```
然后编译:
```shell
python setup.py build_ext --inplace
```
在你需要调用的地方:
```python
# main.py
import add
print add.add(1,-1)
```

## 使用Cython语法
### 定义变量
使用`cdef`来定义变量,结构体,常量.
```python
cdef int i, *j, k[100]
cdef struct node:
    int key
    float value
cdef enum:
    const = 1
cdef bint flag # bool类型使用bint代替
```
你可以用一个cdef来把他们写到一起:
```python
cdef:
    cdef struct node:
        int key
        float value
    int i, *j, k[100]
    void add(int x, int y):
        return x + y
```
还可以使用`ctypedef`来定义类型名称
```python
ctypedef long long LL
```
### 函数
在Cython中有3种函数定义:
- `def`: 传入python对象,返回python对象,直接调用
- `cdef`: 传入python对象或C/C++值,返回python对象或C/C++值,不可直接调用
- `cpdef`: 以上两者的混合   
注意:只有`def`和`cpdef`定义的函数在编译后可以在python代码中直接调用,`cdef`定义的函数则不能.
不过你可以使用`def`来对外封装:
```python
def fib_cdef(int n):
    cdef int fib_in_c(int n):
        if n < 2:
            return n
        return fib_in_c(n-2) + fib_in_c(n-1)
    return fib_in_c(n)
```
那么这3个函数性能如何呢,可以看[这篇评测](http://notes-on-cython.readthedocs.org/en/latest/fibo_speed.html)    

{{ alert('结论: 使用cdef会变得更快,基本和直接用C差不多', type='info') }} 

然而使用`cdef`报错不能很好的捕获异常.你可以这样使用
```python
cdef int divide(int x, int y) except 0:
    ...
```
这样当该函数内部出错时,将会返回一个0.(所以此时应当避免正确的情况中有返回0的可能,以避免歧义.)

### 参数传递
如上所示,传递一个值是很简单的,只要稍稍注意一下它的类型.在python和C/C++之间有一些自动的类型转换:
```python
+-------------------------------------------------------------------------------------------+
|                C types                          |  From Python types  |  To Python types  |  
| [unsigned] char [unsigned] short int, long      |  int, long          |    int            | 
| unsigned int unsigned long [unsigned] long long |  int, long          |    long           |  
| float, double, long double                      |  int, long, float   |    float          |   
| char*                                           |  str/bytes          |    str/bytes      | 
| struct                                          |                     |    dict           | 
+-------------------------------------------------------------------------------------------+
```
由于python的变量是动态类型,解析起来会很慢,所以建议将其显示的指定为C/C++静态类型来提升效果,具体可以看[这篇](http://docs.cython.org/src/quickstart/cythonize.html)  
所谓指定静态类型,就是显示的指定变量的类型.
```python
cdef func(x,y):
    ...
cdef int func(int x, int y):
    ...
```
{{ alert('结论: 指定静态类型大约有35%的提速', type='info') }}   

另一方面,如果需要检测传入的参数不是`None`的话可以加上`not None`来检测
```python
def func(x not None):
    ...
```


如果要向C传递一个数组来处理,大部分情况下应该是numpy的array,推荐使用Memoryview来接受python传入的numpy的array
```python
cdef int[:,:,:] view = np.arange(27, dtype=np.dtype("i")).reshape((3, 3, 3))
cdef int x[3][3][3]
cdef int[:,:,:] view = x
cdef int[:, :, ::1] c_contiguous = c_contig # C的按行存储
cdef int[::1, :, :] f_contiguous = f_contig # Fortran的按列存储

cpdef histogram(int[:,:] image):
    import numpy as np
    cdef int[:] hist = np.zeros((256,),dtype=np.intc)
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            hist[image[x,y]] += 1
    return np.asarray(hist)
```
你几乎可以像使用numpy的array一样的使用Memoryview,不过仍然有一些限制,[详细内容](http://docs.cython.org/src/userguide/memoryviews.html)  
在一些较老的资料中,你也许会见到像下面这样的写法:
```python
def func(np.ndarray[unsigned char, ndim=2, mode="c"] array not None):
    ...
```
{{ alert('虽然很明显,但还是得多加注意,Memoryview和array一样,在函数内做了修改,其原值也会修改.', type='danger') }}   

至于python的list和dict,我个人习惯直接使用,而不指定静态类型.你也可以看看[这个问题](http://stackoverflow.com/questions/1528691/idiomatic-way-to-do-list-dict-in-cython?rq=1)下面的一些关于如何优雅的在Cython中使用list和dict的讨论.

### C++和面向对象
在Cython中也可以方便的使用面向对象的方式工作,只要使用`cdef class`就能在Cython中像在pure Python中那样使用类(当然还是有些限制):
```python
cdef class Rect:
    cdef int width, height
    def __init__(self, int w, int h):
        self.width = w
        self.height = h
    def area(self):
        return self.width*self.height

def test_it(int x, int y):
    cdef Rect R = Rect(x,y)
    return R.area()
```
值得注意的是,Cython中的类可以被pure Python中的类继承,但反过来不行.  
你还可以像下面这样设置一些属性的getter和setter
```python
class shop:
    cdef object goods
    def __cinit__(self):
        self.goods = []
    property goods:
        def __get__(self):
            return "We have: %s" % self.goods
        def __set__(self, value):
            self.goods.append(value)
        def __del__(self):
            del self.goods[:]
```
上面还涉及到`__cinit__`这个方法和原生python的`__init__`有些区别,前者可以更快的执行,官方的例子是:
```python
cdef class Penguin:
    cdef object food

    def __cinit__(self, food):
        self.food = food

    def __init__(self, food):
        print("eating!")

normal_penguin = Penguin('fish')
fast_penguin = Penguin.__new__(Penguin, 'wheat')  # note: not calling __init__() !
```
所以最求效率的化,尽量使用`__cinit__`吧.对于经常创建/删除实例的类,可以在前面加上`@cython.freelist(n)`的装饰器.可以获得更好的性能.   

如果想使用C++中的STL的话,可以像下面这样:
```python
from libcpp.vector cimport vector

cdef vector[int] vect
cdef int i
for i in range(10):
    vect.push_back(i)
for i in range(10):
    print vect[i]

vect = xrange(1,10)
```
python到C++容器的转换规则是
```python
+-------------------------------------------------+
|   Python type  =>   C++ type  => Python type    |
|bytes           |  std::string |   bytes         |
|iterable        |  std::vector |   list          |  
|iterable        |  std::list   |   list          | 
|iterable        |  std::set    |   set           | 
|iterable(len 2) |  std::pair   |   tuple (len 2) |
--------------------------------------------------+
```


## 直接使用C/C++代码
如果你恰好已经有了C部分的代码,想直接在python中调用而不是用cython自己重写的话,你只需要写一个.pyx进行简单的封装,就能达到目的.

### 封装
**如果只是一些C的函数需要封装进来**  
使用`cdef extern`可以把C代码中的函数声明到cython中:
```python
cdef extern int add(int x, int y)

def add_py(int x, int y):
    return add(x, y)
```
当然你得有一个.c的文件来实现add函数  

**若是有一些C++的类需要封装进来**  
举个官方的例子,你有一个rectangle.h的头文件,
```cpp
//rectangle.h

namespace shapes {
    class Rectangle {
    public:
        int x0, y0, x1, y1;
        Rectangle(int x0, int y0, int x1, int y1);
        int getArea();
    };
}
```
一个rectangle.cpp的实现
```cpp
//rectangle.cpp

#include "Rectangle.h"
namespace shapes {
    Rectangle::Rectangle(int X0, int Y0, int X1, int Y1) {
        x0 = X0;
        y0 = Y0;
        x1 = X1;
        y1 = Y1;
    }
    int Rectangle::getArea() {
        return (x1 - x0) * (y1 - y0);
    }
}
```
那么你还需要一个\_rectangle.pyx文件
```python
# _rectangle.pyx

cdef extern from "Rectangle.h" namespace "shapes":
    cdef cppclass Rectangle:
        Rectangle(int, int, int, int) except +
        int x0, y0, x1, y1
        int getArea()

def func():
    cdef Rectangle *rec = new Rectangle(1, 2, 3, 4)
    try:
        recLength = rec.getLength()
        ...
    finally:
        del rec     # delete heap allocated object
```
`func()`就是对外提供的接口.当然如果要对外提供整个类的话,可以用`cdef class`把整个类都封装一遍.
{{ alert('pyx文件不要和你的cpp文件重名,不然自动产生的Python-C-API包裹代码会覆盖掉你的源码', type='danger') }}   

### 参数传递
传递一个值是非常简单的,只要注意类型匹配就可以了,你可以参考[numpy的数据类型](http://docs.scipy.org/doc/numpy/user/basics.types.html)来显示的转换它们.   
问题是传一个数组的时候,需要传入一个地址,尤其对于多维数组来说,只能把它们当做一维数组在C中处理
```python
cdef extern void c_nead_array(unsigned short* arrary)

def func_wrapper(int[:,:] array):
    c_nead_array(&array[0,0])
    return array
```
这就传入了一个2d数组的开始地址.这种方式还可以拿来返回输出.因为是传入一个地址.  
另外,如果有需要传入一个引用的话,比如C++的某些情况,不能直接使用`* ptr` 这样做
```python
from cython.operator cimport dereference as deref

cdef extern func(Image img)
cdef Image *imgptr = new Image()
func(deref(imgptr))
```

## 编写setup.py
在你搞定了上述的重写或者封装之后,你就需要写一个setup.py来进行编译了,好把你的C/C++模块编进共享库文件中.关于setup.py的一般写法,可以看[这里](https://docs.python.org/2/distutils/setupscript.html),不过在Cython中,还是有些区别的.
如果你只有一个pyx文件.那么下面这么写就足够了
```python
# setup.py
from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules = cythonize(
       "test.pyx",
       language="c++", ## 如果是C++就需要
      ))
```
不过我个人更建议下面的写法:
```python
# setup.py
from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

extension = Extension(
           "sub",
           sources=["sub.pyx"],
           include_dirs=[numpy.get_include()], # 如果用到numpy
           language="c++",
)

setup(
        cmdclass = {'build_ext': build_ext},
        ext_modules = cythonize(extension),
)
```
上面的写法中我们只需要注意Extension的写法,你可以同时编译多个C/C++扩展.
```python
extensions = [
        Extension(
           "_test",                             # name1
           sources=["_test.pyx", "test.cpp"],   # 如果有cpp源码
           include_dirs=[numpy.get_include()],
           language="c++"),
        Extension(
            "_test2",                           # name2
            source=["_test2.pyx", "test.c"],    # ditto
        )
]
```
{{ alert('Extension的name务必要和.pyx的文件名要保持一致.', type='danger') }}   

最后,你只需要执行setup.py:
```shell
python setup.py build_ext --inplace
```

## 其他
   写于2015年8月7日by septicmk.  
   内容应该足够支持入门了.若版本升级,API变动.或者想有更深入的了解.还得多看看[官方文档](http://docs.cython.org/index.html).  
   若文中有误,欢迎指正 :)


