#!/usr/bin/python3

import argparse
import sys

keywords = '<>#Â£~|+-*/&%^_.,?:$@'

# Cmds
class Env(object):
    def __init__(self):
        self.default = 'default'
        self.stacks = {}
        self.stackTypes = {}

        self.addStack('default', 'Unicode')
        self.addStack('error', 'Unicode')
        self.addStack('errorcode', 'Integer')

    def getStack(self, name=None):
        if name is None:
            return self.stacks[self.default]
        return self.stacks[name]

    def addStack(self, name, stackType):
        self.stacks[name] = []
        self.stackTypes[name] = stackType

    def verifyType(self, name, stackType):
        return self.stackTypes.get(name, None) == stackType

    def getType(self, name):
        return self.stackTypes.get(name, None)

class Cmd(object):
    def codeGen(self, env):
        raise ValueError('codeGen unimplemented')

    def interpret(self, env):
        raise ValueError('interpret unimplemented')

class PushCmd(Cmd):
    def __init__(self, data=None, stack=None):
        self.data = data
        self.stack = stack

    def interpret(self, env):
        if not self.stack:
            self.stack = env.default

        t = env.getType(self.stack)
        if t == 'Integer' or t == 'Unsigned':
            self.data = int(self.data)
        elif t == 'Double':
            self.data = float(self.data)
        elif t == 'Byte':
            self.data = ord(self.data)
        elif t == 'Boolean':
            if self.data.lower() == 'true':
                self.data = True
            else:
                self.data = False
        elif t == 'Unicode':
            self.data = bytes(self.data, 'utf-8').decode('unicode_escape')

        env.stacks[self.stack].append(self.data)

class PopCmd(Cmd):
    def __init__(self, inputstack=None, outputstack=None, wholestack=False):
        self.inputstack = inputstack
        self.outputstack = outputstack
        self.wholestack = wholestack

    def interpret(self, env):
        if not self.inputstack:
            self.inputstack = env.default
        env.stacks[self.outputstack].append(env.stacks[self.inputstack].pop())

class OutCmd(Cmd):
    def __init__(self, stack=None):
        self.stack = stack

    def interpret(self, env):
        if not self.stack:
            self.stack = env.default

        t = env.getType(self.stack)
        separator = ''
        if t == 'Integer' or t == 'Unsigned' or t == 'Double' or t == 'Boolean':
            separator = ' '
            data = separator.join(['%s' % x for x in env.stacks[self.stack]])
        elif t == 'Byte':
            # FIXME
            pass
        else:
            data = separator.join(env.stacks[self.stack])
        env.stacks[self.stack] = []
        sys.stdout.write(data)
        #print (data)

class StackCmd(Cmd):
    def __init__(self, stack=None, stackType=None, create=False):
        self.stack = stack
        self.stackType = stackType
        self.create = create

    def interpret(self, env):
        if self.create:
            env.addStack(self.stack, self.stackType)

        if not self.stack:
            env.default = 'default'
        else:
            env.default = self.stack

class Oper(Cmd):
    def __init__(self, oper, stack=None):
        self.oper = oper
        self.stack = stack

    def interpret(self, env):
        res = None
        if not self.stack:
            self.stack = env.default
        s = env.stacks[self.stack]
        res = s[0]
        s = s[1:]
        for i in s:
            if self.oper == '+':
                res += i
            elif self.oper == '-':
                res -= i
            elif self.oper == '*':
                res *= i
            elif self.oper == '/':
                res *= i
            elif self.oper == '%':
                res %= i
            elif self.oper == '^':
                res **= i
            else:
                raise ValueError('Unknown operator: %s' % self.oper)

        env.stacks[self.stack] = [res]

# Parser
def readFile(fname):
    with open(fname, 'r') as fd:
        lines = [x.strip() for x in fd.readlines()]
        return lines

def getUntilCommand(params, idx):
    data = ''
    ll = len(params)
    while idx < ll and params[idx] not in keywords:
        data += params[idx]
        idx += 1
    rest = params[idx:]
    return (data, rest, idx)

def parsePush(params):
    if not params:
        raise ValueError('Push needs to have parameters')

    opos = params.find(':')

    if params[0] == '<':
        stack = None
        datapos = 1
        if opos > 0:
            stack = params[1:opos]
            datapos = opos + 1
        return [PushCmd(data=params[datapos:], stack=stack)]
    else:
        idx = 0
        stack = None
        if opos > 0:
            stack = params[1:opos]
            idx = opos + 1

        (data, rest, idx) = getUntilCommand(params, idx)
        v = [PushCmd(data=data, stack=stack)]
        if rest:
            v += parseCmds(rest)
        return v

def parsePop(params):
    inputstack = None
    outputstack = None
    wholestack = False

    opos = params.find(':')
    if opos > 0:
        inputstack = params[1:opos]
        datapos = opos + 1

    if params[0] == '>':
        wholestack = True

    (outputstack, rest, idx) = getUntilCommand(params, 0)
    v = [PopCmd(inputstack=inputstack, outputstack=outputstack, wholestack=wholestack)]
    if rest:
        v += parseCmds(rest)
    return v

def parseOut(params):
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [OutCmd(data)]
    if rest:
        res += parseCmds(rest)
    return res

def parseStack(params):
    if not params:
        return [StackCmd()]
    opos = params.find(':')
    stackType = None
    if opos > 0:
        stackType = params[0:opos]
        idx = opos + 1
    (stack, rest, idx) = getUntilCommand(params, idx)
    res = [StackCmd(stack=stack, stackType=stackType, create=(stackType and stack))]
    res += parseCmds(rest)
    return res

def parseSimpleOper(oper, params):
    if not params:
       raise ValueError("Stack name needed")
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [Oper(oper, data)]
    if rest:
        res += parseCmds(rest)
    return res

def parseBinaryOper(oper, params):
    if not params:
       raise ValueError("Binary operator and stack name needed")
    return parseSimpleOper(oper + params[0], params[1:])

def parseCmds(line):
    cmds = []
    if not line:
        return cmds

    cmd = line[0]
    if cmd == '<':
        cmds += parsePush(line[1:])
    elif cmd == '>':
        cmds += parsePop(line[1:])
    elif cmd == '.':
        cmds += parseOut(line[1:])
    elif cmd == '|':
        cmds += parseStack(line[1:])
    elif cmd in '+-*/%^':
        cmds += parseSimpleOper(cmd, line[1:])
    elif cmd == '0':
        cmds += parseBinaryOper(cmd, line[1:])
    else:
        raise ValueError('Invalid command: %s' % line)

    return cmds

def parseLines(lines):
    cmds = []
    for l in lines:
        cmds += parseCmds(l)

    return cmds

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bizarre compiler')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump intermediate')
    parser.add_argument('-r', '--run', action='store_true', help='Interpret code')
    parser.add_argument('source_file')

    args = parser.parse_args()

    #if len(sys.argv) <= 1:
    #    print('Usage: %s source' % sys.argv[0])
    #    sys.exit(1)

    #lines = readFile(sys.argv[1])
    lines = readFile(args.source_file)
    res = parseLines(lines)
    if args.dump:
        print(res)
    if args.run:
        env = Env()
        for i in res:
            i.interpret(env)
