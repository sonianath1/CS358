#onia Nath - CS358 - Final Interpreter Project
# This file will have a domain extension of 
# images. 


from dataclasses import dataclass
from PIL import Image as pimage

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | ImageLit | Merge | Rotate | And | Or | Not | Eq | Lt | If | LetFun | App
type Value = int | bool | ImageValue | Closure

@dataclass
class Add():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"

@dataclass
class Sub():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"

@dataclass
class Mul():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"

@dataclass
class Div():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"

@dataclass
class Neg():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(- {self.subexpr})"

@dataclass
class Lit():
    value: int
    def __str__(self) -> str:
        return f"{self.value}"

@dataclass
class Let():
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Name():
    name:str
    def __str__(self) -> str:
        return self.name

@dataclass
class Or():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return  f"({self.left} or {self.right})"

@dataclass
class And():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"

@dataclass
class Not():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"
@dataclass
class Eq():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} == {self.right})"

@dataclass
class Lt():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} < {self.right})"

@dataclass
class If():
    cond: Expr
    then: Expr
    _else: Expr
    def __str__(self) -> str:
        return f"(if {self.cond} then {self.then} else {self._else})"

@dataclass
class LetFun():
    name: str
    param: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name} ({self.param}) = {self.bodyexpr} in {self.inexpr} end"


@dataclass
class App():
    fun: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"({self.fun} ({self.arg}))"


#----------------- IMAGE ----------------------------
@dataclass
class ImageLit():
    name: str
    def __str__(self) -> str:
        return f"img({self.name})"

@dataclass
class ImageValue():
    image: pimage.Image
    def __str__(self) -> str:
        return f"img({self.image.show})"

@dataclass
class Merge():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"(merge {self.left} and {self.right})"


@dataclass
class Rotate():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(Rotate {self.subexpr} by 90 degrees)"

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length 


@dataclass
class Closure:
    param: str
    body: Expr
    env: Env[Value]


from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment env with a new binding from name to value'''
    return ((name,value),) + env

def lookupEnv[V](name: str, env: Env[V]) -> (V | None) :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    # exercises2b.py shows a different implementation alternative
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _ :
            return None        

class EvalError(Exception):
    pass


def eval(e: Expr) -> Value:
    return evalInEnv((), e)


def evalInEnv(env: Env[int], e:Expr) -> Value:
    match e:

        case Add(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (bool(), _) | (_, bool()):
                    raise EvalError("addition of non-integers")
                case (int(lv), int(rv)):
                    return lv + rv
                case _:
                    raise EvalError("addition of non-integers")

        case Sub(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (bool(), _) | (_, bool()):
                    raise EvalError("subtraction of non-integers")
                case (int(lv), int(rv)):
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")

        case Mul(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            match (lv, rv):
                case (bool(), _) | (_, bool()):
                    raise EvalError("multiplication of non-integers")
                case (int(lv), int(rv)):
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")

        case Div(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (bool(), _) | (_, bool()):
                    raise EvalError("division of non-integers")
                case (int(lv), int(rv)):
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers")                

        case Neg(s):
            match evalInEnv(env,s):
                case bool(b):
                    raise EvalError("negation of non-integer")
                case int(i):
                    return -i
                case _:
                    raise EvalError("negation of non-integer")

        case Lit(lit):
            match lit:  # two-level matching keeps type-checker happy
                case bool(b):
                    return b
                case int(i):
                    return i
                case _:
                    raise EvalError(f"unknown literal type: {type(lit)}")
        case Not(s):
            match evalInEnv(env, s):
                case bool(b):
                    return not b
                case _:
                    raise EvalError("not of non boolean")

        case And(l,r):
            match evalInEnv(env,l): # only evaulate left first 
                case bool(lv):
                    if not lv:
                        return False # short circuit
                    match evalInEnv(env, r):
                        case bool(rv):
                            return rv # returns if either false or true
                        case _:
                            raise EvalError("and of non boolean")
                case _:
                    raise EvalError("and of non boolena")

        case Or(l, r):
            match evalInEnv(env,l):
                case bool(lv):
                    if lv:
                        return True # short circuit, only one has to be true
                    match evalInEnv(env,r):
                        case bool(rv):
                            return rv
                        case _:
                            raise EvalError("or of non boolean")
                case _:
                    raise EvalError("or of non boolean")

        case Eq(l, r):
            lv = evalInEnv(env, l)
            rv = evalInEnv(env, r)
            if type(lv) != type(rv):
                return False
            match (lv, rv):
                case (ImageValue(il), ImageValue(ir)):
                    return il.height == ir.height  # compare height of images
                case (int(a), int(b)):
                    return a == b
                case (bool(a), bool(b)):
                    return a == b
                case _:
                    raise EvalError("equal on incorrec type")

        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v

        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)

        case Lt(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (bool(), _) | (_, bool()):
                    raise EvalError("Less than operator of bool types")
                case (int(lv), int (rv)):
                    return lv < rv
                case _:
                    raise EvalError("lt requires two integers")

        case If(b, t, e):
            match evalInEnv(env, b):
                case bool(bv):
                    if bv:
                        return evalInEnv(env, t)   # only evaluate t if True
                    else:
                        return evalInEnv(env, e)   # only evaluate e if False
                case _:
                    raise EvalError("if condition must be a boolean")

        case LetFun(n,p,b,i):
            c = Closure(p,b,env)
            newEnv = extendEnv(n,c,env)
            c.env = newEnv    
            return evalInEnv(newEnv,i)

        case App(f,a):
            fun = evalInEnv(env,f)
            arg = evalInEnv(env,a)
            match fun:
                case Closure(p,b,cenv):
                    newEnv = extendEnv(p,arg,cenv) 
                    return evalInEnv(newEnv,b)
                case _:
                    raise EvalError("application of non-function")

        # Image cases
        case ImageLit(n):
            image = pimage.open(n)
            return ImageValue(image)

        case Merge(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (ImageValue(le), ImageValue(ri)):
                    if le.height != ri.height:
                        raise EvalError("image must have same height")
                    merge = pimage.new('RGB', (le.width + ri.width, le.height))
                    merge.paste(le, (0, 0))
                    merge.paste(ri, (le.width, 0))
                    return ImageValue(merge)
                case _:
                    raise EvalError("merge requires 2 images")

        case Rotate(s):
            match evalInEnv(env, s):
                case ImageValue(image):
                    return ImageValue(image.rotate(90))
                case _:
                    raise EvalError("rotate requires an image")
'''
a = (Sub(Lit(10) , True))
print(a)
print(eval(a))
'''
def run(e: Expr):
    result = eval(e)
    match result:
        case bool(b):
            print(b)
        case int(i):
            print(i)
        case ImageValue(img):
            img.save("answer.png")
            img.show()  # opens a viewer automatically
'''
Domain Specific Extension: Images

This extension is images. It allows users to:

    - load images from files
    - merge them to be side by side (if height equals for both)
    - rotate them by 90 degress

Whatever you choose to do with the images, it is saved in "answer.png"
and can be viewed in the diectory. 

I want to credit Prof Yao Li for his interp_arith_turtle.py template.
It was helpful in getting this project done and understanding how to 
use match cases with an interpreter.

To run the tests, uncomment it at the bottom of the file. It was getting annoying 
to have images generate when i was just trying to test some functions
in command line so I commented them out to make testing less annoying. 

To test with the Pillow Pakcage, make sure to have the latest version of python and then run:

    pip3 install Pillow

I have inclided a beautiful photo meant for testing purposes. The testing below
references it. If you comment out line 377, that test should trigger an exception due to
the photos not being the same height.

It worjs
'''

'''
# test loading a single image
run(ImageLit("images/cutephoto.jpg"))

# test rotating
run(Rotate(ImageLit("images/cutephoto.jpg")))


run(Merge(ImageLit("images/cutephoto.jpg"), ImageLit("images/cutephoto.jpg")))

# test using let with images
run(Let("x", ImageLit("images/cutephoto.jpg"), Rotate(Name("x"))))

# test merging two images
#run(Merge(ImageLit("images/cutephoto.jpg"), ImageLit("images/pfp.jpg"))) '''
#ID: /(?!img$)(?!rotate$)(?!merge$)(?!true$)(?!false$)[a-zA-Z_][a-zA-Z0-9_]*/

