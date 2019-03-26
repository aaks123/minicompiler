#!/usr/bin/python
import yacc
import lexer # our lexer
tokens = lexer.tokens
from subprocess import call
import sys
import tac
import symbolTable
programLineOffset = 0
haltExecution = False
# file_input: (NEWLINE | stmt)* ENDMARKER
def p_file_input(p):
	"""file_input :	single_stmt ENDMARKER
	"""
	p[0] = p[1]
	print("executing p_file_input")
	TAC.emit(ST.getCurrentScope(), '','', -1, 'HALT')
	ST.addAttributeToCurrentScope('numParam', 0)
	ST.removeCurrentScope()
	# TAC.printCode()
	# ST.printSymbolTableHistory()

# Our temporary symbol
def p_single_stmt(p):
	"""single_stmt	:	single_stmt NEWLINE
					|
	"""
	print("executing p_single_input")
	if len(p) == 3:
		p[0] = p[1]
	else:
		p[0] = []

def p_single_stmt1(p):
	"""single_stmt	:	single_stmt stmt
	"""
	print("executing p_single_input")
	p[0] = p[1] + [p[2]]


# funcdef: [decorators] 'def' NAME parameters ':' suite
def p_funcdef(p):
    """funcdef : DEF NAME MarkerScope parameters MarkerArg COLON NEWLINE INDENT single_stmt DEDENT
    """
    # TAC.noop(ST.getCurrentScope(), p[9]['beginlist'])
    # TAC.noop(ST.getCurrentScope(), p[9]['endlist'])
    TAC.emit(ST.getCurrentScope(), '', '', '', 'JUMP_RETURN')
    ST.removeCurrentScope()
    p[0] = dict()
    p[0]['type'] = 'FUNCTION'
    p[0]['reference'] = p[3]['reference']


def p_MarkerScope(p):
	"""MarkerScope 	:
	"""
	p[0] = dict()
	p[0]['reference'] = p[-1]
	if ST.existsInCurrentScope(p[0]['reference']):
		error('Redefinition', p[0]['reference'])
	else:
		ST.addIdentifier(p[0]['reference'], 'FUNCTION')
		level = ST.getAttribute(p[-1], 'scopeLevel')
		offset = ST.getAttribute(p[-1], 'offset')
		place = ST.getNewTempVar((level, offset), p[-1])
		ST.addAttribute(p[-1], ST.getCurrentScope(), place)
		ST.addAttribute(p[-1], 'reference', p[0]['reference'])
		TAC.emit(ST.getCurrentScope(), place, p[0]['reference'], '', '=REF')
		ST.addScope(p[0]['reference'], place)
		TAC.createNewFucntionCode(p[0]['reference'])

def p_MarkerArg(p):
	"""MarkerArg 	:
	"""
	for arg in p[-1]:
		if ST.existsInCurrentScope(arg):
			error('Redefinition', arg)
		else:
			ST.addIdentifier(arg, 'NUMBER')
			level = ST.getAttribute(arg, 'scopeLevel')
			offset = ST.getAttribute(arg, 'offset')
			place = ST.getNewTempVar((level, offset), arg, True)
			ST.addAttribute(arg, ST.getCurrentScope(), place)
	ST.addAttributeToCurrentScope('numParam', len(p[-1]))

# parameters: '(' [varargslist] ')'
def p_parameters(p):
	"""parameters 	: LPAREN RPAREN 
					| LPAREN varargslist RPAREN"""
	if len(p) == 3:
		p[0] = []
	else:
		p[0] = p[2]

def p_function_call(p):
	"""function_call 	: NAME LPAREN RPAREN 
						| NAME LPAREN testlist RPAREN 
	"""
	p[0] = dict()
	if not ST.exists(p[1]):
		error('Reference', p[1])
	else :
		identifierType = ST.getAttribute(p[1], 'type')
		if identifierType == 'FUNCTION':
			place = ST.getAttribute(p[1], 'var')
			# if place == None:
			# 	if not ST.existsInCurrentScope(p[1]):
			# 		level = ST.getAttribute(p[1], 'scopeLevel')
			# 		offset = ST.getAttribute(p[1], 'offset')
			# 		ST.addAttribute(p[1], ST.getCurrentScope(), place)
			# 	else:
			# 		place = ST.getAttribute(p[1], 'var')

			if len(p)==4:
				pass
			else:
				for param in p[3]:
					TAC.emit(ST.getCurrentScope(), param['place'], '', '', 'PARAM')

			TAC.emit(ST.getCurrentScope(), '', '', place, 'JUMPLABEL')
			reference = ST.getAttribute(p[1], 'reference')
			p[0]['type'] = ST.getAttributeFromFunctionList(reference, 'returnType')
			returnPlace = ST.getNewTempVar()
			TAC.emit(ST.getCurrentScope(), returnPlace, '', '', 'FUNCTION_RETURN')
			p[0]['place'] = returnPlace
		else :
			error('Reference', p[1])
	p[0]['type'] = 'NUMBER'
	# p[0]['type'] = 'UNDEFINED'
#varargslist: fpdef ['=' test] (',' fpdef ['=' test])* 
def p_varargslist(p):
	"""varargslist 	: fpdef
					| fpdef EQUAL test
	"""
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		error('Default paramater not supported', p)

def p_varargslistext(p):
	"""varargslist 	: fpdef COMMA varargslist
					| fpdef EQUAL test COMMA varargslist
	"""
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		error('Default paramater not supported', p)
		

# fpdef: NAME | '(' fplist ')'
def p_fpdef(p):
	"""fpdef 	: NAME 
				| LPAREN fplist RPAREN
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		error('Tupled paramater not supported', p)
		

# fplist: fpdef (',' fpdef)* [',']
def p_fplist(p):
	"""fplist 	: fpdef
				| fpdef COMMA fplist	
	"""
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		error('Function Parameter not supported in this way', p)


# stmt: simple_stmt | compound_stmt
def p_stmt(p):
	"""stmt 	: simple_stmt
		
				| compound_stmt
	"""
	print("executing stmt")
	p[0] = p[1]

# simple_stmt: small_stmt  NEWLINE

def p_simple_stmt(p):
	"""simple_stmt 	: small_stmts NEWLINE
	"""
	print("executing simple stmt")
	p[0] = p[1]

def p_small_stmts(p):
	"""small_stmts 	: small_stmt
	"""
	print("executing small stmts")
	p[0] = p[1]

# small_stmt: 	expr_stmt 	| print_stmt   	| 
#			  	pass_stmt 	| flow_stmt 	|assert_stmt|
#    			import_stmt | global_stmt 	
## CHANGING GRAMMAR : pass, import, global, assert : not urgent
def p_small_stmt(p):
	"""small_stmt 	: flow_stmt Marker
					| expr_stmt Marker
					| print_stmt Marker
	"""
	print("executing small stmt")
	p[0] = p[1]
	TAC.backpatch(ST.getCurrentScope(), p[1].get('nextlist', []), p[2]['quad'])


# expr_stmt: testlist (augassign testlist | ('=' testlist)*)
# def p_expr_stmt(p):
# 	"""expr_stmt 	: testlist augassign testlist
# 					| testlist eqtestlist
# 	"""
## CHANGING GRAMMAR : Removing fancy operations
## CHANGING GRAMMAR : Removing list assignment multiple
	
def p_expr_stmt(p):
	"""expr_stmt 	: test EQUAL test
					| test EQUAL function_call
	"""
	print("executing expr stmt")	
	p[0] = dict()
	place = ''
	try:
		p[1]['isArray']
		try:
			# a[i] = b[j]
			p[3]['isArray']
			if p[1]['type'] != p[3]['type']:
				error('Type', p)
			absAddrLeft = p[1]['absAddr']
			value = ST.getNewTempVar()
			TAC.emit(ST.getCurrentScope(), value, p[3]['place'], '', '=')
			TAC.emit(ST.getCurrentScope(), absAddrLeft, value, '', 'SW')
		except:
			# a[i] = x
			if p[1]['type'] != p[3]['type']:
				error('Type', p)
			absAddr = p[1]['absAddr']
			# TAC.emit(ST.getCurrentScope(), absAddr, baseAddr, relativeAddr, '+')
			try:
				TAC.emit(ST.getCurrentScope(), absAddr, p[3]['place'], '', 'SW')
			except:		
				error('Reference', p)
		
	except:
		if haltExecution:
			sys.exit()
		try:
			# x = a[i]
			p[3]['isArray']
			value = ST.getNewTempVar()
			TAC.emit(ST.getCurrentScope(), value, p[3]['absAddr'], '', 'LW')

			if ST.exists(p[1]['name']):
				ST.addAttribute(p[1]['name'], 'type', p[3]['type'])
				if ST.existsInCurrentScope(p[1]['name']):
					place = ST.getAttribute(p[1]['name'], ST.getCurrentScope())
				else:
					place = ST.getNewTempVar()
					ST.addAttribute(p[1]['name'], ST.getCurrentScope(), place)
			else:
				ST.addIdentifier(p[1]['name'], p[3]['type'])
				place = ST.getNewTempVar()
				ST.addAttribute(p[1]['name'], ST.getCurrentScope(), place)
			p[0]['nextlist'] = []
			TAC.emit(ST.getCurrentScope(),place, value, '', '=')


		except:
			# x = y
			isList = False
			try:
				p[3]['isList']
				p[1]['isList'] = True
				isList = True
			except:
				pass

			try:
				p[1]['name']
			except:
				error("Cannot assign to constant", p)
			if ST.exists(p[1]['name']):
				ST.addAttribute(p[1]['name'], 'type', p[3]['type'])
				if ST.existsInCurrentScope(p[1]['name']):
					place = ST.getAttribute(p[1]['name'], ST.getCurrentScope())
				else:
					level = ST.getAttribute(p[1]['name'], 'scopeLevel')
					offset = ST.getAttribute(p[1]['name'], 'offset')
					place = ST.getNewTempVar((level, offset), p[1]['name'])
					ST.addAttribute(p[1]['name'], ST.getCurrentScope(), place)
				TAC.emit(ST.getCurrentScope(), place, p[3]['place'], '', '=')
			else:
				# declaration
				ST.addIdentifier(p[1]['name'], p[3]['type'])
				# p[1]['place'] = ST.getNewTempVar()
				# place = p[1]['place']
				p[1]['place'] = p[3]['place']
				level = ST.getAttribute(p[1]['name'], 'scopeLevel')
				offset = ST.getAttribute(p[1]['name'], 'offset')
				ST.changeMemLocation(p[1]['place'], (level, offset), p[1]['name'])
				ST.addAttribute(p[1]['name'], ST.getCurrentScope(), p[1]['place'])
				ST.addAttribute(p[1]['name'], 'reference', p[1]['reference'])

			p[0]['nextlist'] = []
			# TODO : may need in case of array
			# try:
			# 	if isList:
			# 		TAC.emit(ST.getCurrentScope(),place, p[3]['name'], 'ARRAY', '=')
			# 	else:
			# 		TAC.emit(ST.getCurrentScope(),place, p[3]['place'], '', '=')
			# except:		
			# 	error('Reference', p)


# print_stmt: 'print' [ test (',' test)* [','] ]
def p_print_stmt(p):
	"""print_stmt 	:	PRINT
					|	PRINT testlist
	"""
	p[0] = dict()
	if len(p)==2:
		TAC.emit(ST.getCurrentScope(), '', '', '', 'PRINT')
	else:
		for item in p[2]:
			itemType = item.get('type')
			if itemType not in ['STRING', 'NUMBER', 'BOOLEAN', 'UNDEFINED']:
				error('Print', p)
			TAC.emit(ST.getCurrentScope(), item['place'], '', itemType, 'PRINT')
			TAC.emit(ST.getCurrentScope(), '', '', '', 'PRINT')


# flow_stmt: break_stmt | continue_stmt | return_stmt 
def p_flow_stmt(p):
	"""flow_stmt 	: break_stmt Marker
					| return_stmt Marker
	"""
	p[0] = p[1]
	TAC.backpatch(ST.getCurrentScope(), p[1].get('nextlist', []), p[2]['quad'])


def p_flow_stmt2(p):
	"""flow_stmt 	: continue_stmt Marker
	"""
	p[0] = p[1]
	TAC.backpatch(ST.getCurrentScope(), p[1].get('beginlist', []), p[2]['quad'])

# break_stmt: 'break'
def p_break_stmt(p):
	"""break_stmt 	: BREAK
	"""
	p[0] = dict()
	p[0]['endlist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), '', '', -1, 'GOTO')

# continue_stmt: 'continue'
def p_continue_stmt(p):
	"""continue_stmt 	: CONTINUE
	"""
	p[0] = dict()
	p[0]['beginlist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), '', '', -1, 'GOTO')

# return_stmt: 'return' [testlist]
def p_return_stmt(p):
	"""return_stmt 	:	RETURN 
					|	RETURN test
	"""
	p[0] = dict()
	p[0]['type'] = 'NUMBER'
	if len(p) == 2:
		ST.addAttributeToCurrentScope('returnType', 'NUMBER')
		TAC.emit(ST.getCurrentScope(), '0', '', '', 'RETURN')				
	else:
		returnType = ST.getAttributeFromCurrentScope('returnType')
		if returnType == 'UNDEFINED':
			if p[2]['type'] == 'FUNCTION':
				ST.addAttributeToCurrentScope('returnType', 'UNDEFINED')
			else:
				ST.addAttributeToCurrentScope('returnType', p[2]['type'])
		elif p[2]['type'] != returnType:
			error('Type', p)
		else:
			pass
		TAC.emit(ST.getCurrentScope(), p[2]['place'], '', '', 'RETURN')

# compound_stmt: if_stmt | while_stmt | for_stmt | funcdef | classdef 
def p_compound_stmt(p):
	"""compound_stmt 	: if_stmt Marker
						| for_stmt Marker
						| while_stmt Marker
						| funcdef Marker
						| function_call Marker
	"""
	p[0] = p[1]
	nextlist = p[1].get('nextlist',[])
	TAC.backpatch(ST.getCurrentScope(), nextlist, p[2]['quad'])

# if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]

def p_if_stmt(p):
	"""if_stmt 	:	IF test COLON MarkerIf suite
				|	IF test COLON MarkerIf suite ELSE COLON MarkerElse suite
	"""
	p[0] = dict()
	
	if p[2]['type'] != 'BOOLEAN':
		# print 1
		error('Type', p)

	if len(p) == 6:
		p[0]['nextlist'] = TAC.merge(p[4].get('falselist', []), p[5].get('nextlist', []))
		p[0]['beginlist'] = p[5].get('beginlist', [])
		p[0]['endlist'] = p[5].get('endlist', [])
	else:
		TAC.backpatch(ST.getCurrentScope(), p[4]['falselist'], p[8]['quad'])
		p[0]['nextlist'] = p[8]['nextlist']
		p[0]['beginlist'] = TAC.merge(p[9].get('beginlist', []), p[5].get('beginlist', []))
		p[0]['endlist'] = TAC.merge(p[9].get('endlist', []), p[5].get('endlist', []))


# while_stmt: 'while' test ':' suite
def p_while_stmt(p):
	"""while_stmt 	:	WHILE Marker test COLON MarkerWhile suite 
	"""
	if p[3]['type'] != 'BOOLEAN':
		error('Type', p)
	
	p[0] = dict()
	p[0]['type'] = 'VOID'
	p[0]['nextlist'] = []
	TAC.backpatch(ST.getCurrentScope(), p[6]['beginlist'], p[2]['quad'])
	p[0]['nextlist'] = TAC.merge(p[6].get('endlist', []), p[6].get('nextlist', []))
	p[0]['nextlist'] = TAC.merge(p[5].get('falselist', []), p[0].get('nextlist', []))
	TAC.emit(ST.getCurrentScope(),'', '', p[2]['quad'], 'GOTO')
 
def p_Marker(p):
	"""Marker 		:	
	"""
	p[0] = dict()
	p[0]['quad'] = TAC.getNextQuad(ST.getCurrentScope())

def p_MarkerWhile(p):
	"""MarkerWhile 	:
	"""
	p[0] = dict()
	p[0]['falselist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), p[-2]['place'], 0, -1,'COND_GOTO') 

def p_MarkerIf(p):
	"""MarkerIf 	:
	"""
	p[0] = dict()
	p[0]['falselist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), p[-2]['place'], 0, -1, 'COND_GOTO')

def p_MarkerElse(p):
	"""MarkerElse 	:
	"""
	p[0] = dict()
	p[0]['nextlist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), '', '', -1, 'GOTO')
	p[0]['quad'] = TAC.getNextQuad(ST.getCurrentScope())


# for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]

def p_for_stmt(p): 
	"""for_stmt 	:	FOR atom IN test COLON MarkerFor suite
	"""
	p[0] = dict()
	p[0]['nextlist'] = TAC.merge(p[7].get('endlist', []), p[7].get('nextlist', []))
	p[0]['nextlist'] = TAC.merge(p[6].get('falselist', []), p[0].get('nextlist', []))
	TAC.emit(ST.getCurrentScope(), p[6]['index'], p[6]['index'], 1, '+')
	TAC.emit(ST.getCurrentScope(),'', '', p[6]['quad'], 'GOTO')

def p_MarkerFor(p):
	"""MarkerFor : 
	"""
	p[0] = dict()
	place = ''
	# print p[-2]
	try:
		p[-2]['isList']
	except:
		error('Not an array', p[-2])
	if ST.exists(p[-4]['name']):
		place = p[-4]['place']
		p[-4]['type'] = p[-2]['type']
	else:
		ST.addIdentifier(p[-4]['name'], p[-2]['type'])
		place = ST.getNewTempVar()
		ST.addAttribute(p[-4]['name'], ST.getCurrentScope(), place)
	index = ST.getNewTempVar()
	TAC.emit(ST.getCurrentScope(), index, 0, '', '=')
	array = ST.getNewTempVar()
	TAC.emit(ST.getCurrentScope(), array, p[-2]['place'], 'ARRAY', '=')
	size = len(p[-2]['place'])
	length = ST.getNewTempVar()
	TAC.emit(ST.getCurrentScope(), length, size, '', '=')
	condition = ST.getNewTempVar()
	p[0]['quad'] = TAC.getNextQuad(ST.getCurrentScope())
	TAC.emit(ST.getCurrentScope(), condition, index, length, '==')
	p[0]['falselist'] = [TAC.getNextQuad(ST.getCurrentScope())]
	TAC.emit(ST.getCurrentScope(), condition, 1, -1, 'COND_GOTO')

	width = ST.getWidthFromType(p[-2]['type'])
	baseAddr = ST.getBaseAddress(ST.getCurrentScope(), p[-2]['name'])
	relativeAddr = ST.getNewTempVar()
	TAC.emit(ST.getCurrentScope(), relativeAddr, index, width, '*')
	absAddr = ST.getNewTempVar()
	TAC.emit(ST.getCurrentScope(), absAddr, baseAddr, relativeAddr, '+')
	TAC.emit(ST.getCurrentScope(), place, absAddr, '', 'LW')


	# TAC.emit(ST.getCurrentScope(), place, array+'['+index+']', '', '=')
	p[0]['index'] = index
	# suite will add code here
	# then add GOTO condition check line in for_stmt
	# patch this -1 in compound_stmt by merging its falselist in for_stmt


# suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
def p_suite(p):
	"""suite 	: simple_stmt
				| NEWLINE INDENT stmts DEDENT"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = p[3]
		# print "here"


#TODO
def p_array(p):
	"""test 	: test_expr 
	"""
	print("executing array")
	if len(p) == 2:
		p[0] = p[1]
		p[0]['reference'] = p[1].get('reference')
	else :
		if p[3]['type'] != 'NUMBER':
			error('Reference', p)
		else:
			try:
				p[1]['isIdentifier']
			except:
				error('Reference', p[1])
			# set values to propagate above uptil test = test.
			# to handle a[i] = x, x = a[i] and a[i] = a[j]
			p[0] = dict()
			p[0]['name'] = p[1]['name']
			p[0]['type'] = p[1]['type']
			p[0]['isArray'] = True
			p[0]['place'] = p[3]['place']			
			

# test: or_test
def p_test(p):
	"""test_expr 	: or_test
	"""
	p[0] = p[1]


# or_test: and_test ('or' and_test)*
def p_or_test(p):
	"""or_test 	: and_test
				| and_test OR or_test
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		# print p[1]
		if p[1]['type'] == p[3]['type'] == 'BOOLEAN':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'BOOLEAN'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference3', p)
			error('Type', p)		

# and_test: not_test ('and' not_test)*
def p_and_test(p):
	"""and_test 	: not_test
					| not_test AND and_test
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'BOOLEAN':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'BOOLEAN'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# not_test: 'not' not_test | comparison
def p_not_test(p):
	"""not_test 	: NOT not_test
					| comparison
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[2]['type'] == 'BOOLEAN':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'BOOLEAN'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[2]['place'],'', p[1])
		else:
			if(p[2]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			# print 4
			error('Type', p)

def p_comparision(p):
	"""comparison 	: 	expr
					|	expr comp_op expr
	"""
	if len(p)==2:
		p[0] = p[1]
	elif len(p)==4:
		if p[1]['type'] in ['NUMBER', 'BOOLEAN', 'UNDEFINED'] and  p[3]['type'] in ['NUMBER', 'BOOLEAN', 'UNDEFINED']:
			pass
			# okay : Nothing to do here
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			# print 5
			error('Type', p)
		p[0] = dict()
		p[0]['type'] = 'BOOLEAN'
		p[0]['place'] = ST.getNewTempVar()
		TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])

# comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
## CHANGING GRAMMAR : Withdrawing support of IN and IS
def p_comp_op(p):
	"""comp_op 	: LESS
				| GREATER
				| EQEQUAL
				| GREATEREQUAL
				| LESSEQUAL
				| NOTEQUAL
	"""
	p[0] = p[1]

# expr: xor_expr ('|' xor_expr)*
def p_expr(p):
	"""expr 	: xor_expr
				| xor_expr VBAR expr
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'NUMBER':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# xor_expr: and_expr ('^' and_expr)*
def p_xor_expr(p):
	"""xor_expr 	: and_expr
					| and_expr CIRCUMFLEX xor_expr
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'NUMBER':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# and_expr: shift_expr ('&' shift_expr)*
def p_and_expr(p):
	"""and_expr 	: shift_expr
					| shift_expr AMPER and_expr
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'NUMBER':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# shift_expr: arith_expr (('<<'|'>>') arith_expr)*
def p_shift_expr(p):
	"""shift_expr 	: arith_expr
					| arith_expr LEFTSHIFT shift_expr
					| arith_expr RIGHTSHIFT shift_expr
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'NUMBER':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# arith_expr: term (('+'|'-') term)*
def p_arith_expr(p):
	"""arith_expr 	:	term
					|	term PLUS arith_expr
					|	term MINUS arith_expr
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] in ['NUMBER', 'BOOLEAN', 'UNDEFINED'] and  p[3]['type'] in ['NUMBER', 'BOOLEAN', 'UNDEFINED']:
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(),p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)


# term: factor (('*'|'/'|'%'|'//') factor)*
def p_term(p):
	"""term :	factor
			|	factor STAR term
			|	factor SLASH term
			|	factor PERCENT term
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		if p[1]['type'] == p[3]['type'] == 'NUMBER':
			p[0] = dict()
			p[0]['place'] = ST.getNewTempVar()
			p[0]['type'] = 'NUMBER'
			TAC.emit(ST.getCurrentScope(), p[0]['place'], p[1]['place'], p[3]['place'], p[2])
		else:
			if(p[1]['type']=='REFERENCE_ERROR' or p[3]['type']=='REFERENCE_ERROR'):
				error('Reference', p)
			error('Type', p)

# factor: ('+'|'-') factor | power
def p_factor(p):
	"""factor 	: power
				| PLUS factor
				| MINUS factor
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		if p[2]['type'] != 'NUMBER':
			error('Type', p)
		p[0] = dict()
		p[0]['place'] = ST.getNewTempVar()
		p[0]['type'] = 'NUMBER'
		TAC.emit(ST.getCurrentScope(), p[0]['place'], 0, p[2]['place'], '-')
# power: atom trailer*
def p_power(p):
	"""power 	: atom
				| atom LSQB test RSQB

	"""
	if len(p) == 2:
		p[0] = p[1]
	else :
		if p[3]['type'] != 'NUMBER':
			error('Reference', p)
		else:
			try:
				p[1]['isIdentifier']
			except:
				error('Reference', p[1])
			# set values to propagate above uptil test = test.
			# to handle a[i] = x, x = a[i] and a[i] = a[j]
			p[0] = dict()
			# p[0]['name'] = p[1]['name']
			p[0]['type'] = p[1]['type']
			# p[0]['isArray'] = True
			# p[0]['place'] = p[3]['place']
			try:
				# p[1]['isArray']
				# TODO add adtribute to isArray to NAME in symbol table
				width = ST.getWidthFromType(p[1]['type'])
				baseAddr = ST.getBaseAddress(ST.getCurrentScope(), p[1]['name'])
				index = ST.getNewTempVar()
				TAC.emit(ST.getCurrentScope(), index, p[3]['place'], '', '=')
				relativeAddr = ST.getNewTempVar()
				TAC.emit(ST.getCurrentScope(), relativeAddr, index, width, '*')
				absAddr = ST.getNewTempVar()
				TAC.emit(ST.getCurrentScope(), absAddr, baseAddr, relativeAddr, '+')
				value = ST.getNewTempVar()
				TAC.emit(ST.getCurrentScope(), value, absAddr, '', 'LW')
				p[0]['place'] = value
				p[0]['absAddr'] = absAddr
				p[0]['isArray'] = True
				p[0]['name'] = p[1]['name']
			except:
				error('Reference', p[1])


def p_atom1(p):
	'''atom :	NAME
	'''
	p[0] = dict()
	# p[0]['place'] = p[1]
	if ST.exists(p[1]):
		p[0]['name'] = p[1]
		p[0]['type'] = ST.getAttribute(p[1], 'type')
		p[0]['place'] = ST.getAttribute(p[1], ST.getCurrentScope())
		p[0]['isIdentifier'] = True
		try:
			p[0]['isList'] = ST.getAttribute(p[1], 'isList')
		except:
			pass
		# TODO may need to add more keys like offset and scopename
	else:
		p[0]['name'] = p[1]
		p[0]['type'] = 'REFERENCE_ERROR'


	# need to do symbol table thing, type attribution
def p_atom2(p):
	'''atom :	NUMBER
	'''
	p[0] = dict()
	p[0]['type'] = 'NUMBER'
	name = ST.getNewTempVar()
	ST.addIdentifier(name, 'NUMBER')
	level = ST.getAttribute(name, 'scopeLevel')
	offset = ST.getAttribute(name, 'offset')

	p[0]['place'] = ST.getNewTempVar((level, offset), name)
	TAC.emit(ST.getCurrentScope(), p[0]['place'], p[1], '', '=i')
	# need to do symbol table thing, type attribution

def p_atom3(p):
	"""atom		:	STRING
				|	TRIPLESTRING
	"""
	p[0] = dict()
	p[0]['type'] = 'STRING'
	p[0]['place'] = p[1]

def p_atom4(p):
	'''atom :	FNUMBER
	'''
	p[0] = dict()
	p[0]['type'] = 'NUMBER'
	p[0]['place'] = p[1]

def p_atom5(p):
	'''atom :	LSQB RSQB
			| 	LSQB listmaker RSQB
	'''
	p[0] = dict()
	if len(p)==3:
		p[0]['place'] = []
		p[0]['type'] = 'NUMBER'
	else:
		p[0] = p[2]
	p[0]['isList'] = True
	p[0]['name'] = ST.getNewTempVar()
	ST.addIdentifier(p[0]['name'], p[0]['type'])
	ST.addAttribute(p[0]['name'], 'place', p[0]['place'])
	ST.addAttribute(p[0]['name'], 'isArray', 'True')

	TAC.emit(ST.getCurrentScope(), p[0]['name'], p[0]['place'], 'ARRAY', '=')
	# print p[0]

def p_atom6(p): 
	"""atom	:	LPAREN RPAREN
			| 	LPAREN testlist_comp RPAREN
	"""
	if len(p) == 3:
		p[0] = dict()
	else:
		p[0] = p[2]
# listmaker: test (',' test)* [','] 
def p_listmaker(p):
	"""listmaker 	: test
					| test COMMA listmaker
	"""
	p[0] = dict()
	if len(p) == 2:
		try:
			p[0]['place'] = [p[1]['place']]
			p[0]['type'] = p[1]['type']
		except:
			error('Reference', p)
	else:
		if p[3]['type'] != p[1]['type']:
			error('Type', p)
		else:
			try:
				p[0]['place'] = [p[1]['place']] + p[3]['place']
				p[0]['type'] = p[1]['type']
			except:
				error('Reference', p)

# testlist_comp: test (',' test)* [','] 
def p_testlist_comp(p):
	"""testlist_comp 	: test
						| test COMMA testlist_comp
	"""
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = [p[1]] + p[2]
		# Not very sure.

# testlist: test (',' test)* [',']
def p_testlist(p):
	"""testlist 	: test
					| test COMMA testlist
	"""
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]


# classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
# def p_classdef(p):
# 	"""classdef 	: CLASS NAME COLON suite
# 					| CLASS NAME LPAREN RPAREN COLON suite
# 					| CLASS NAME LPAREN testlist RPAREN COLON suite
# 	"""
# 	error('SYNTAX', p)

def p_stmts(p):
	"""stmts 	: stmt stmts
				| stmt Marker"""
	p[0] = dict()
	p[0]['beginlist'] = TAC.merge(p[1].get('beginlist', []), p[2].get('beginlist', []))
	p[0]['endlist'] = TAC.merge(p[1].get('endlist', []), p[2].get('endlist', []))

def p_error(p):
	global haltExecution
	haltExecution = True
	try:
		print("Syntax Error near '"+str(p.value)+ "' in line "+str(p.lineno - programLineOffset))
	except:
		try:
			print("Syntax Error in line "+str(p.lineno - programLineOffset))
		except:
			print("Syntax Error")
	sys.exit()

def error(errorType, p):
	global haltExecution
	haltExecution = True
	try:
		print(errorType +" Error near '"+str(p.value)+"' in line "+str(p.lineno - programLineOffset))
	except:
		try:
			print(errorType + " Error in line "+str(p.lineno - programLineOffset))
		except:
			print(errorType + " Error")
	sys.exit()

class G1Parser(object):
	def __init__(self, mlexer=None):
		if mlexer is None:
			mlexer = lexer.G1Lexer()
		self.mlexer = mlexer
		self.parser = yacc.yacc(start="file_input", debug=True)
	def parse(self, code):
		# initializeTF()	
		self.mlexer.input(code)
		self.parser.parse(lexer = self.mlexer, debug=True)
		return ST, TAC
		
def initializeTF():
	scopeName = ST.getCurrentScope()
	ST.addIdentifier('True', 'BOOLEAN')
	ST.addAttribute('True', scopeName, 1)
	ST.addIdentifier('False', 'BOOLEAN')
	ST.addAttribute('False', scopeName, 0)

ST = symbolTable.SymbolTable()
TAC = tac.ThreeAddressCode()
