# Image-Interpreter
An image interpreter for a simple image language


# The Core language features:
Arithmetics: Lit(int) | Add | Sub | Mul | Div | Neg|
boolean Lit(bool) | And | Or | Not
binding variables Let | Name
eqaulity Eq 
relation: Lf | If

expresion = Add | Sub | Mul | Div | Neg | And | Not | Or| Eq | Lt | If | Lit | Let | Name | ImgComb | RotImage |



Image specific extension: ImgComb | RotImage | Lit(filename) |
  * ImgComb : feature that will combine two images
  * RotImage: will prefrom a rotation on a image
  * value : ruster file in jpg or png

The domain extension are going to be used to modify the images given. 
