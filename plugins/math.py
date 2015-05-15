#!/usr/bin/env python3

DEBUG = False
from collections import namedtuple
import re
sm = staticmethod
depth = 0
def staticmethod(func):
  _=[sm(func)]
  def newFunc(*a, **b):
    global depth
    f=_[0]
    print(" |" * depth, func, a, b)
    depth += 1
    res = func(*a,**b)
    depth -= 1
    print(" |" * depth, res)
    return res
  return newFunc

if not DEBUG:
  staticmethod = sm


class TokenStream:
  def __init__(self, line):
    self.pos = 0
    self.toks = list(filter(bool,re.split(r"(\d*\.\d+|\d+|\w+|_|.)", line)))
    self.toks.append("<END>")

  def peek(self):
    return self.toks[self.pos]

  def get(self):
    t = self.toks[self.pos]
    self.pos += 1
    return t

  def unget(self):
    self.pos -= 1

  def __str__(self):
    return str(self.pos) + str(self.toks)
  def __repr__(self):
    return str(self)

def Error(msg, stream):
  lines = stream.toks[:-1]
  valid = "".join(lines[:stream.pos])
  invalid = "".join(lines[stream.pos:])
  raise Exception("{{GREEN}}{}{{RED}}<{}>{{GREEN}}{}".format(valid, msg, invalid))

def optional(cls, toks):
  t = toks.pos
  val = cls.parse(toks)

  if val is not None:
    return val

  toks.pos = t
  return None


class Assignment:
  @staticmethod
  def parse(line):
    var = optional(VariableAssignment, line)
    if var is not None:
      return var

    func = optional(FunctionalAssignment, line)
    if func is not None:
      return func

    return Expression.parse(line)

class VariableAssignment(namedtuple('VariableAssignment', ['name', 'expr'])):
  @staticmethod
  def parse(line):
    name = line.get()
    if not name.isalpha():
      return None
    if line.get() != '=':
      return None
    expr = Assignment.parse(line)
    if expr is None:
      return None
    return VariableAssignment(name, expr)

  def evaluate(self, scope):
    scope[self.name] = self.expr.evaluate(scope)
    return scope[self.name]

  def __str__(self): return "{}={}".format(self.name, self.expr)

class FunctionalAssignment(namedtuple('FunctionalAssignment', ['name', 'args', 'expr'])):
  @staticmethod
  def parse(line):
    name = line.get()

    if not name.isalpha():
      return None
    if line.get() != '(':
      return None

    args = []
    arg = line.get()
    if arg != ')':
      # (name ',') (name ')')
      while True:
        if not arg.isalpha():
          return None
        args.append(arg)

        arg = line.get()
        if arg ==')':
          break;
        if arg ==',':
          arg = line.get()

    if line.get() != "=":
        return None

    expr = Assignment.parse(line)
    if expr is None:
      return None
    return FunctionalAssignment(name, args, expr)

  def evaluate(self, scope):
    scope[self.name] = self
    return Atom(None, self.name).evaluate(scope)


  def call(self, args):
    if len(args) != len(self.args):
        return None
    nscope = scope.copy()
    nscope.update(dict(zip(self.args, [
            n.evaluate(scope) for n in args])))
    return self.expr.evaluate(nscope)

  def __str__(self):
    return "{}({})={}".format(self.name, ",".join(self.args), self.expr)

class NativeFunction:
  def __init__(self, name, func):
    self.name = name;
    self.func = func
  def evaluate(self, scope):
    scope[self.name] = self
    return self

  def call(self, args):
    vals = [e.evaluate(scope) for e in args]
    return self.func(*vals)

  def __str__(self):
    return self.name

#class MuliExpr(namedtuple('MuliExpr', ['head', 'tail'])):

class Expression(namedtuple('Expression', ['head', 'tail'])):
  @staticmethod
  def parse(line):
    head = Term.parse(line)
    if head is None:
      return None

    tail = []
    while True:
      op = line.get()
      if op not in "+-":
        line.unget()
        break
      val = Term.parse(line)
      if val is None:
        raise Error("Expected atom", line)

      tail.append((op, val))

    if not tail:
      return head
    return Expression(head, tail)

  def evaluate(self, scope):
    val = self.head.evaluate(scope)
    for (mod, term) in self.tail:
      v = term.evaluate(scope)
      if mod == '+':
        val += v
      elif mod == '-':
        val -= v
      else:
        raise("error")
    return val

  def __str__(self):
    return "{}{}".format(self.head, "".join([
      "{}{}".format(*t) for t in self.tail
    ]))

class Term(namedtuple('Term', ['head', 'tail'])):
  @staticmethod
  def parse(line):
    head = Factor.parse(line)
    if head is None:
      return None

    tail = []
    while True:
      op = line.get()
      if op not in "*/%":
        line.unget()
        break
      val = Factor.parse(line)
      if val is None:
        raise "Expected atom"
      tail.append((op, val))
    if tail:
      return Term(head, tail)
    return head

  def evaluate(self, scope):
    val = self.head.evaluate(scope)
    for (mod, term) in self.tail:
      v = term.evaluate(scope)
      if mod == '*':
        val *= v
      elif mod == '/':
        val /= v
      elif mod == '%':
        val %= v
      else:
        raise("error")
    return val

  def __str__(self):
    return "{}{}".format(self.head, "".join([
      "{}{}".format(*t) for t in self.tail
    ]))

class Factor(namedtuple('Factor', ['base', 'exp'])):
  @staticmethod
  def parse(line):
    head = Value.parse(line)
    if head is None:
      return None

    tok = line.get()
    if tok != '^':
      line.unget()
      return head

    exp = Factor.parse(line)
    return Factor(head, exp)


  def evaluate(self, scope):
    return self.base.evaluate(scope) ** self.exp.evaluate(scope)

class Value(namedtuple('Value', ['base', 'mod', 'tail'])):
  @staticmethod
  def parse(line):
    mod = line.get()
    if mod not in "-":
      line.unget()
      mod = None
    base = Atom.parse(line)
    if base is None:
      return None

    tail = []
    while True:
        t = optional(Tail, line)
        if t is None:
            break
        tail.append(t)

    if not mod and not tail:
      return base
    return Value(base, mod, tail)

  def evaluate(self, scope):
    val = self.base.evaluate(scope)
    for t in self.tail:
        val = t.evaluate(scope,val)

    if self.mod == '-':
      val *= -1
    return val

  def __str__(self):
    out = []
    if self.mod:
        out.append("-")
    out.append(str(self.base))
    out.extend(self.tail)
    return "".join([str(x) for x in out])

class Tail(namedtuple('Tail', ['args'])):
    @staticmethod
    def parse(line):
        val = line.get()
        if val != '(':
            line.unget()
            return None
        args = []
        while True:
            val = optional(Expression, line)
            if val is None:
                return None

            args.append(val)
            val = line.get()

            if val == ')':
                return Tail(args)
            elif val != ',':
                raise Error("Unclosed Function call", line)

    def evaluate(self, scope, func):
        if type(func) in [FunctionalAssignment, NativeFunction]:
            # self.args contains the expression trees for the arguments
            return func.call(self.args)
        return None

    def __str__(self):
        return "({})".format(",".join([str(x) for x in self.args]))

class Atom(namedtuple('Atom', ['value', 'name'])):
  @staticmethod
  def parse(line):
    tok = line.get()
    if tok == "(":
      line.unget()
      return Parens.parse(line)
    if tok.isalpha():
      return Atom(None, tok)
    try:
      return Atom(float(tok), None)
    except:
      pass
    if tok == "<END>":
      raise Error("Incomplete expression", line)
    raise Error("Unexpected token", line)

  def __str__(self):
      return str(self.value) if self.value is not None else self.name

  def evaluate(self, scope):
    if self.value is not None:
      return self.value
    return scope.get(self.name, 0)

class Parens(namedtuple('Parens',['tree'])):
  @staticmethod
  def parse(line):
      tok = line.get()
      if tok != '(':
        return None

      val = Assignment.parse(line)
      if val is None:
        raise Error("Invalid sub expression", line)

      tok = line.get()
      if tok != ')':
          raise Error("Unclosed ')'", line)
      return val


def evaluate(line):
  stream = TokenStream(line.replace(" ",""))
  tree = Assignment.parse(stream)

  if stream.peek() != '<END>':
    raise Error("Incomplete parse", stream)

  if tree is None:
      return None
  global scope
  return tree.evaluate(scope)

import math
scope = {
  "sin": NativeFunction("sin", math.sin)
}
for name in dir(math):
  attr = getattr(math, name)
  if callable(attr):
    scope[name] = NativeFunction(name, attr)
  elif type(attr) == float:
    scope[name] = attr


import api

@api.onPrivmsg()
def math(sender, message, target):
  if not message.startswith("%"):
    return
  if message.startswith("%_%"):
    return
  equ = message[1:].replace(" ","")
  try:
    value = evaluate(equ)
    if value is not None:
        api.privmsg(target, "{GREEN}" + str(round(value,15)))
  except Exception as e:
    api.privmsg(target, str(e))
    raise
