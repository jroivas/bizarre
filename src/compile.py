#!/usr/bin/python3

import argparse
import sys

keywords = '<>#Â£~|+-*/&%^_.,?:$@'

# Cmds
class Env(object):
    def __init__(self):
        self.default = 'default'
        self.result = 'result'
        self.stacks = {}
        self.stackTypes = {}
        self.labels = {}
        self.index = 0

        self.addStack(self.default, 'Unicode')
        self.addStack(self.result, 'Boolean')
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

    def formIndex(self, cmds):
        for i, cmd in enumerate(cmds):
            #print (cmd, isinstance(cmd, LabelCmd))
            if isinstance(cmd, LabelCmd):
                self.labels[cmd.name] = i
        #print ('LBL %s' % self.labels)

class Cmd(object):
    def codeGen(self, env):
        raise ValueError('codeGen unimplemented')

    def interpret(self, env):
        raise ValueError('interpret unimplemented')

class PushCmd(Cmd):
    def __init__(self, data=None, stack=None):
        self.data = data
        self.stack = stack

    def __repr__(self):
        return 'Push(%s <- %s)' % (self.stack, self.data)

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

    def __repr__(self):
        return 'Pop(%s -> %s)' % (self.inputstack, self.outputstack)

    def interpret(self, env):
        if not self.inputstack:
            self.inputstack = env.default

        data = env.stacks[self.inputstack].pop()
        if self.outputstack != '0':
            env.stacks[self.outputstack].append(data)

class CastCmd(Cmd):
    def __init__(self, inputstack=None, outputstack=None):
        self.inputstack = inputstack
        self.outputstack = outputstack

    def __repr__(self):
        return 'Cast(%s -> %s)' % (self.inputstack, self.outputstack)

    def interpret(self, env):
        if not self.inputstack:
            self.inputstack = env.default

        src_type = env.getType(self.inputstack)
        dst_type = env.getType(self.outputstack)

        data = env.stacks[self.inputstack][-1]
        if dst_type == 'Integer' or dst_type == 'Unsigned':
            data = int(data)
        elif dst_type == 'Double':
            data = float(data)
        elif dst_type == 'Byte':
            data = ord(data)
        elif dst_type == 'Boolean':
            data = bool(data)
        elif dst_type == 'Unicode':
            if (src_type == 'Integer' or
                src_type == 'Unsigned' or
                src_type == 'Boolean' or
                src_type == 'Double'):
                data = '%s' % data
            elif src_type == 'Byte':
                data = chr(data)
            else:
                data = bytes(data, 'utf-8').decode('unicode_escape')

        env.stacks[self.outputstack].append(data)

class StackSizeCmd(Cmd):
    def __init__(self, inputstack=None, outputstack=None):
        self.inputstack = inputstack
        self.outputstack = outputstack

    def __repr__(self):
        return 'StackSize(%s -> %s)' % (self.inputstack, self.outputstack)

    def interpret(self, env):
        if not self.inputstack:
            self.inputstack = env.default

        data = len(env.stacks[self.inputstack])
        env.stacks[self.outputstack].append(data)


class OutCmd(Cmd):
    def __init__(self, stack=None):
        self.stack = stack

    def __repr__(self):
        return 'Out(%s)' % (self.stack)

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

class DupCmd(Cmd):
    def __init__(self, stack=None):
        self.stack = stack

    def __repr__(self):
        return 'Dup(%s)' % (self.stack)

    def interpret(self, env):
        if not self.stack:
            self.stack = env.default

        env.stacks[self.stack].append(env.stacks[self.stack][-1])

class StackCmd(Cmd):
    def __init__(self, stack=None, stackType=None, create=False):
        self.stack = stack
        self.stackType = stackType
        self.create = create

    def __repr__(self):
        return 'Stack(%s, %s)' % (self.stack, self.stackType)

    def interpret(self, env):
        if self.create:
            env.addStack(self.stack, self.stackType)

        if not self.stack:
            env.default = 'default'
        else:
            env.default = self.stack

class OperCmd(Cmd):
    def __init__(self, oper, stack=None):
        self.oper = oper
        self.stack = stack

    def __repr__(self):
        return 'Oper(%s, %s)' % (self.oper, self.stack)

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

class LabelCmd(Cmd):
    def __init__(self, name):
        self.name = name

    def interpret(self, env):
        pass
        #env.labels[self.name] = self

    def __repr__(self):
        return 'Label(%s)' % (self.name)

class GotoCmd(Cmd):
    def __init__(self, name):
        self.name = name

    def interpret(self, env):
        goto = False
        if env.stacks[env.result]:
            goto = env.stacks[env.result].pop()
        else:
            goto = True

        if goto:
            env.index = env.labels.get(self.name, None)
            if env.index is None:
                raise ValueError('Goto target not found')

    def __repr__(self):
        return 'Goto(%s)' % (self.name)

class CondCmd(Cmd):
    def __init__(self, oper, stack=None):
        self.oper = oper
        self.stack = stack

    def interpret(self, env):
        if not self.stack:
            self.stack = env.default

        s = env.stacks[self.stack]
        res = False

        if self.oper == '?':
            res = bool(s)
        elif self.oper == '<':
            res = s[-2] < s[-1]
        elif self.oper == '<=':
            res = s[-2] <= s[-1]
        elif self.oper == '>':
            res = s[-2] > s[-1]
        elif self.oper == '>=':
            res = s[-2] >= s[-1]
        elif self.oper == '=':
            res = s[-2] == s[-1]
        elif self.oper == '!':
            res = s[-2] != s[-1]
        elif self.oper == '0':
            res = s[-1] == 0
        elif self.oper == '-':
            res = s[-1] < 0
        else:
            raise ValueError('Invalid stack operator: %s' % self.oper)

        env.stacks[env.result].append(res)

    def __repr__(self):
        return 'Cond(%s, %s)' % (self.oper, self.stack)

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
    #if not params:
    #    raise ValueError('Push needs to have parameters')

    opos = params.find(':')

    if params and params[0] == '<':
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
            stack = params[0:opos]
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
    idx = 0
    if params and params[0] == '>':
        wholestack = True
        idx += 1

    datapos = 0
    if opos > 0:
        inputstack = params[idx:opos]
        datapos = opos + 1
        idx = 0

    (outputstack, rest, idx) = getUntilCommand(params[datapos:], idx)
    if not outputstack:
        raise ValueError('Output stack not defined while pop!')

    v = [PopCmd(inputstack=inputstack, outputstack=outputstack, wholestack=wholestack)]
    if rest:
        v += parseCmds(rest)
    return v

def parseCast(params):
    inputstack = None
    outputstack = None
    wholestack = False

    opos = params.find(':')
    idx = 0
    datapos = 0
    if opos > 0:
        inputstack = params[idx:opos]
        datapos = opos + 1
        idx = 0

    (outputstack, rest, idx) = getUntilCommand(params[datapos:], idx)
    if not outputstack:
        raise ValueError('Output stack not defined while casting!')

    v = [CastCmd(inputstack=inputstack, outputstack=outputstack)]
    if rest:
        v += parseCmds(rest)
    return v

def parseStackSize(params):
    inputstack = None
    outputstack = None
    wholestack = False

    opos = params.find(':')
    idx = 0
    datapos = 0
    if opos > 0:
        inputstack = params[idx:opos]
        datapos = opos + 1
        idx = 0

    (outputstack, rest, idx) = getUntilCommand(params[datapos:], idx)
    if not outputstack:
        raise ValueError('Output stack not defined while stacksize!')

    v = [StackSizeCmd(inputstack=inputstack, outputstack=outputstack)]
    if rest:
        v += parseCmds(rest)
    return v


def parseDup(params):
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [DupCmd(data)]
    if rest:
        res += parseCmds(rest)
    return res

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
    idx = 0
    if opos > 0:
        stackType = params[0:opos]
        idx = opos + 1
    (stack, rest, idx) = getUntilCommand(params, idx)
    res = [StackCmd(stack=stack, stackType=stackType, create=(stackType and stack))]
    res += parseCmds(rest)
    return res

def parseSimpleOper(oper, params):
    #if not params:
    ##   raise ValueError("Stack name needed")
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [OperCmd(oper, data)]
    if rest:
        res += parseCmds(rest)
    return res

def parseBinaryOper(oper, params):
    if not params:
       raise ValueError("Binary operator and stack name needed")
    return parseSimpleOper(oper + params[0], params[1:])

def parseLabel(params):
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [LabelCmd(data)]
    if rest:
        res += parseCmds(rest)
    return res

def parseGoto(params):
    (data, rest, idx) = getUntilCommand(params, 0)
    res = [GotoCmd(data)]
    if rest:
        res += parseCmds(rest)
    return res

def parseConditional(params):
    if not params:
        raise ValueError('Expected conditional type')
    condType = params[0]
    (stack, rest, idx) = getUntilCommand(params[1:], 0)
    res = [CondCmd(condType, stack)]
    if rest:
        res += parseCmds(rest)
    return res

def parseCmds(line):
    cmds = []
    if not line:
        return cmds

    cmd = line[0]
    if cmd == '#':
        # Comment so pass until EOL
        pass
    elif cmd == '<':
        cmds += parsePush(line[1:])
    elif cmd == '>':
        cmds += parsePop(line[1:])
    elif cmd == '£':
        cmds += parseCast(line[1:])
    elif cmd == '.':
        cmds += parseOut(line[1:])
    elif cmd == '_':
        cmds += parseDup(line[1:])
    elif cmd == '|':
        cmds += parseStack(line[1:])
    elif cmd in '+-*/%^':
        cmds += parseSimpleOper(cmd, line[1:])
    elif cmd == '0':
        cmds += parseBinaryOper(cmd, line[1:])
    elif cmd == ':':
        cmds += parseLabel(line[1:])
    elif cmd == '$':
        cmds += parseGoto(line[1:])
    elif cmd == '?':
        cmds += parseConditional(line[1:])
    elif cmd == '~':
        cmds += parseStackSize(line[1:])
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
        env.formIndex(res)
        size = len(res)
        while env.index < size:
            #print (res[env.index])
            res[env.index].interpret(env)
            env.index += 1
            #print (env.stacks)
