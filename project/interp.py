
from PIL import Image
import subprocess
import os
from dataclasses import dataclass

#defining the literal values
type Value = int | Raster | bool

#definig an expresion

type Expr =  Add | Sub | Mul | Div | Neg | Lit | Let | Name | Or | Not | And | Eq | Lt | If | ImgComb | RotImag


@dataclass
class ImgComb():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"(combining {self.left} with {self.right})"

@dataclass
class RotImag():
    subexpre : Expr 
    def __str__(self)->str:
        return f"(rotated image {self.subexpre})"

@dataclass
class Raster():
    img : Image.Image #giving it a pillow object
    def __str__(self)->str:
        return f"{self.img}"

#------ Core Language features -----
@dataclass
class Add():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"

@dataclass
class Sub():
    left : Expr
    right: Expr
    def __str__(self)-> str:
        return f"({self.left} - {self.right})"
    
@dataclass 
class Mul():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"

@dataclass
class Div():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"

@dataclass
class Neg():
    subexpr : Expr
    def __str__(self) -> str:
        return f"(-{self.subexpr})"

@dataclass
class Lit():
    value : Value
    def __str__(self) -> str:
        return f"{self.value}"

@dataclass
class Let():
    name : str
    defexpr : Expr
    bodyexpr : Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Name():
    name : str
    def __str__(self) -> str:
        return self.name


@dataclass
class Or():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} or {self.right})"

@dataclass
class And():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"

@dataclass
class Not():
    subexpr : Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"

@dataclass 
class If():
    cond : Expr
    thenexpr : Expr
    elseexpr : Expr
    def __str__(self) -> str:
        return f"(if {self.cond} then {self.thenexpr} else {self.elseexpr})"
    
@dataclass
class Eq():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} == {self.right})"

@dataclass
class Lt():
    left : Expr
    right : Expr
    def __str__(self) -> str:
        return f"({self.left} < {self.right})"



#---- Enviroment section
type Binding[V] = tuple[str, V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...]  # this tuple type has arbitrary length

from typing import Any

emptyEnv: Env[Any] = ()  # the empty environment has no bindings


def extendEnv[V](name: str, value: V, env: Env[V]) -> Env[V]:
    """Return a new environment that extends the input environment
    env with a new binding from name to value"""
    return ((name, value),) + env


def lookupEnv[V](name: str, env: Env[V]) -> V | None:
    """Return the first value bound to name in the input environment env
    (or raise an exception if there is no such binding)"""
    match env:
        case ((n, v), *rest):
            if n == name:
                return v
            else:
                return lookupEnv(name, rest)  # type: ignore
        case _:
            return None
        
class EvalError(Exception):
    pass

#helper functions to type check values
def isInt(v) -> bool:
    return isinstance(v,int) and not isinstance(v,bool)
def isBool(v) -> bool:
    return isinstance(v,bool)
def isRaster(v) -> bool:
    return isinstance(v,Raster)
def eqRaster(lv : Raster,rv :Raster) -> bool:
    if lv.img.size != rv.img.size: #quick break is checking if they are the same size
        return False
    return lv.img.tobytes() == rv.img.tobytes()
    

def eval(e : Expr) -> Value:
    return evalInEnv(emptyEnv,e)

def evalInEnv(env: Env[Value],e : Expr) -> Value:
    match e:
        case Add(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            if not isInt(lv) or  not isInt(rv):
                raise  EvalError("Arithmetics only done with Integer values")
            return lv + rv
        case Sub(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            if not isInt(lv) or not isInt(rv):
                raise  EvalError("Arithmetics only done with Integer values")
            return lv - rv
        case Mul(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            if not isInt(lv) or  not isInt(rv):
                raise  EvalError("Arithmetics only done with Integer values")
            return lv * rv
        case Div(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            if not isInt(lv) or  not isInt(rv):
                raise  EvalError("Arithmetics only done with Integer values")
            if rv == 0:
                raise EvalError("Can't not divide by zero")
            return lv // rv
        case Neg(s):
            sv = evalInEnv(env,s)
            if not isInt(sv):
                raise EvalError("Negation only allowed on integer")
            return -(sv) 
        case And(l,r):
            lv = evalInEnv(env,l)
            if not isBool(lv):
                raise EvalError("Can't do 'and' with non-boolean values")
            if not lv:
                return False
            rv = evalInEnv(env,r) 
            if not isBool(rv):
                raise EvalError("Can't do 'and' with non-boolean values")
            return rv    
        case Or(l,r):
            lv = evalInEnv(env,l)
            if not isBool(lv):
                raise EvalError("Can't do 'and' with non-boolean values")
            if lv:
                return True
            rv = evalInEnv(env,r) 
            if not isBool(rv):
                raise EvalError("Can't do 'or' with non-boolean values")
            return rv 
        case Not(s):
            sv = evalInEnv(env,s)
            if not isBool(sv):
                raise EvalError("Can't do 'not' with non-boolean values")
            return not(sv)
        case Eq(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)

            if isInt(lv) and isInt(rv):
                return lv == rv
            if isBool(lv) and isBool(rv):
                return lv == rv
            if isRaster(lv) and isRaster(rv):
                return eqRaster(lv,rv)
            return False
        case Lt(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)

            if not isInt(lv) or not isInt(rv):
                raise EvalError(" cannot do '<' with non-integer values")
            return lv < rv 
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v
        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv,b)
        case Lit(lit_v):
            if isinstance(lit_v,str): #user give a string to file 
                try:
                    img1 = Image.open(lit_v).convert("RGBA")
                    return Raster(img=img1) #returning raster with image data
                except Exception as e:
                    raise EvalError(f"could not open file name '{lit_v}': {e}")
            return lit_v
        case If(b,t,e):
            bv = evalInEnv(env,b)
            if not isBool(bv):
                raise EvalError("'if' does not work with non-boolean values")
            if bv:
                return evalInEnv(env,t)
            else:
                return evalInEnv(env,e)
        case ImgComb(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            match lv,rv:
                case Raster(img1),Raster(img2): #case when we have two images
                    if img1.height != img2.height: #cant merge images that have different height
                        raise EvalError("Cant combined images with different height")
                    #creating new canvas to combine the two image
                    w = img1.size[0] + img2.size[0] #getting width for new image
                    h = img1.height 
                    new_image = Image.new("RGBA",(w,h)) #creating empyt canvas with size of the images above

                    new_image.paste(img1,(0,0)) #pasting top left corner
                    new_image.paste(img2,(img1.size[0],0)) # skiping width of first image and aligned with top
                    return Raster(img=new_image) #returns the new image that is a combination of the first two
                case _:
                    raise EvalError("need two images inorder to combine")
        case RotImag(s):
            rot = evalInEnv(env,s)
            if isRaster(rot):
                rotated_image = rot.img.rotate(-90,expand=True)
                return Raster(img=rotated_image)
            raise EvalError("Only allowed to do rotation on images")

def run(e : Expr) -> None:
    print(f"running {e}")
    if os.path.exists("answer.png"):
        os.remove("answer.png")

    try:
        match eval(e):
            case bool(i):
                print(f"result: {i}")
            case int(i):
                print(f"resutl: {i}")
            case Raster(img_data):
                img_data.save("answer.png")
                #opens window viewer on mac, find out how to open on different operators
                subprocess.run(["open","answer.png"])

    except EvalError as err:
        print(err)
            
                
'''
Image DSL 

This DSL extend the core language with image manipulation using the pillow python library.

Feature that were added for image operations
-----------------------------------------------------------------------
Values added: Raster, contains a matrix with image data. This is achieved by pillow library which allows for image objects that correspond with image metadata

Operators: Rotimag, rotates the image by 90 degrees clockwise. ImgComb, takes to image that are the same height and combines them

    rotimag(s) -> returns a Raster with a new image object of the original image rotated by 90 degrees
    ImgComb(l,r) -> returns a Raster with a new image object that contains two images combined side by side.

Usage
--------------------------------
Current design choices allows for execution of image alteration operation. Pillow allows for easy functions calls 
that allow for these image operations.
'''


if __name__ == "__main__":

    #Testing image combination. remove commet block to use
    ''' 
    test_comb = ImgComb(Lit("Img1.jpeg"),Lit("img2.jpeg"))
    run(test_comb)
    '''

    #permission error can occur of image is still open on window, since everytime run is called it deletes answer.png but if window is opend then permission error occurs

    #Testing Image Rotation
    '''
    test_rot = RotImag(Lit("img2.jpeg"))
    run(test_rot)
    '''

    #testing image rotation and img comb togethor -> leads to error because img2 height changes
    '''
    test_bot = ImgComb(Lit("Img1.jpeg"),RotImag(Lit("img2.jpeg")))
    run(test_bot)
    '''

    #testing equality
    '''
    run(Eq(Lit("img2.jpeg"),Lit("img2.jpeg")))
    '''

    #testing if statement
    run(If(
        (Lt(Lit(1),Lit(2))),
        RotImag(Lit("Img1.jpeg")),
        ImgComb(Lit("Img1.jpeg"),Lit("img2.jpeg"))
    ))