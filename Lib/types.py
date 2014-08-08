StringTypes = str,
TupleType = tuple
TypeType = type
IntType = LongType = int	# xxx
FloatType = float
ListType = list
DictionaryType = dict
NoneType = type (None)
BooleanType = bool
StringType = UnicodeType = str	# xxx
ComplexType = XRangeType = None	# xxx
class A: 
	def f (s):
		pass
ClassType= type (A)
MethodType = type (A().f)
FunctionType = type (A.f)
InstanceType = type (A())
import string
ModuleType = type (string)
CodeType = type (A.f.func_code)
BuiltinMethodType = MethodType	# xxx
BuiltinFunctionType = type (abs)
