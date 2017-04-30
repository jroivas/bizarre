# Bizarre

Bizarre is a programming language.

To be more presice, it's a turing tarpit.

## Design

Bizarre is designed to be compact and easy to implement.

Bizarre is heavily stack based.

Errors pushed on specific error stack.
Any invalid character or invalid combination is error.

## Stacknames

Stackname is any string with any alphanum. Stackname can't contain `0`.

## Push to stack

First, simple "Hello, World!"

    <H<e<l<l<o< <W<o<r<l<d<!.

Or simpler version

    <<Hello, World!
    .

To open a bit the syntax, command `<` tells to push data to stack.
Data in this case is Unicode character.

In case of operator `<<` it pushes list of unicode characters until EOL.
Command `.` means print out stack.

## Stacks

Bizarre has multiple stacks.
Default stack is "string based" and everything pushed there
will be presented as a unicode char as seen on previous example.

In the end we have different kind of stacks:

 - Unicode
 - Integer
 - Unsigned (integer)
 - Double (floating point)
 - Byte
 - Boolean

Bizarre has one DEFAULT unicode stack, other stacks must be selected.
By "selected", we mean it must be created.

Every stack has selector, while default being unicode.
Selector command is `|` followed by stack identifier.
To create a totally new stack do following:

    |Integer:num1

Syntax is command `|` followed by type, colon `:` and name of stack.
After this command, proper type stack is created and selected active.

To switch to differenc stack, use selector command again:

    |num1

Difference is, that type is left out, and stack name is followed directly after selector `|`.
It's an error to instruct this for uninitialized stack.
This also means stack types can't be stack names.

After that all push and pop affects to the selected stack.
Bizarre is strongly typed, so pushing wrong kind of value to wrong stack is error.

Default unicode stack can be selected just with empty selector:

    |


## Pop from stack

Similar way pop is basic stack operation.
Pop is oppose of push command: `>`

However since Bizarre does not have any "active memory", registers or temporary variables,
pop target may be questionable.

Idea of pop is to pop to ANOTHER stack.
Thus it's MANDATORY to give stack name after pop.
Let's take an example:

    |Integer:num2
    |Integer:num1
    <10<5<2<1
    >num2
    >num2
    |num2
    .

This creates two Integer stacks, and `num1` is default active stack after init.
We push four numbers to that stack.
After it, we pop two numbers and push them to `num2` stack.
We select `num2` as active stack, and print it's contents.

Similar way, pop until newline:

    |Integer:nums
    >>nums

## Push to specific stack

Simlar way push to specific stack is done by:

    |Integer:num2
    |Integer:num1
    <10
    <num2:5

Thus num1 would contain `10`, and num2 `5`.

## Stack operators

Just pushing and popping is not enough so Bizarre has stack operators.
Valid operators are:

 - `+` to append or add
 - `-` to negate or minus
 - `*` to multiply
 - `/` to divide
 - `%` to modulus
 - `^` to power
 - `0&` to binary and
 - `0|` to binary or
 - `0^` to binary xor
 - `0~` to binary negate
 - `0!` to binary not

All operations might not be possible for all stack types.
Operator without any options applies to current stack,
otherwise specified stack follows operator.

Let's modify our old example:

    |Integer:num2
    |Integer:num1
    <10<5<6<7
    >num2
    >num2
    *num2
    .num2

This would output `42` since `6` and `7` are pushed to num2 stack,
then multiplied, multiply output replaces stack data, and then it's outputted.

## Duplicate

Sometimes one just needs copy of stack data.
Thus we have duplicate operand `_`.
See following example:

    |Integer:num
    <7
    _
    +
    .

Output should be 14, since 7 is duplicated in stack and then summed up and outputted.

## Streams

We have already used output command `.`
It knows data type and outputs it properly to stdout.

To be precise we have also input command `,` which read data from stdin
and puts it to current stack.

As other stack commands, these may define stack as well.
See simple echo:

    ,.

This reads unicode and outputs unicode.
More complex example, reads number (or fail) and outputs (echo) read number:

    |Integer:num
    ,num
    .num

## Errors

Bizarre defines error in many operations.
There could be different strategies to define how to recover error.
However Bizarre leaves it's up to programmer.

Error code is outputted to stack named `errorcode` and it's type is Integer.
Error message is outputted to stack named `error` and it's type is Unicode.
These stacks are not emptyed by default, so it may cumulate multiple errors.

## Emptying stack

Sometimes it might be useful to empty a stack.
Bizarre introduces the simplest way to do it: reintroduction.

Example:

    |Integer:num2
    |Integer:num
    <1<2<5<8<9<10
    >num2
    .num2
    |Integer:num
    >num

This should output only `10`. After this both num and num2 are empty.

## Checking for emptiness

Stack without data is a sad stack.
So we have way to check if stack has data.
It's boolean operator `?`. It's result is stored to `result` stack.

    |Integer:num
    <33
    ?
    .result
    >
    ?
    .result

This should output first `true` followed by `33` and `false`.

## Labels

One can label anything. Label command is colon `:`:

    :label
    <H

Goto is simply dollar `$` and label name:

    :repeat
    <<Hello
    $repeat

Dollar operator checks `result` stack.
If stack is empty, goto is always done, otherwise topmost result defines
if goto is performed or not.

## Comments

Hash is recogniced as comment. Comment continues until end of line.

## Conditionals

What's an programming language without conditionals?

Boolean operator is basic question `?`, which evaluates stack with operand.
Known operands:

 - No operator -> check queue for emptiness
 - `<` second entry is smaller than top entry
 - `<=` second entry is smaller than top entry or equals
 - `>` second entry is bigger than top entry
 - `>=` second entry is bigger than top entry or equals
 - `=` second entry equals to top entry
 - `!` second entry does not equals to top entry
 - `0` top entry is zero
 - `-` top entry is negative

Result is pushed to `result` stack.

Checking result stack is straightforward with
dollar `$`operation. If result is true, go to label.

Let's take example:

    |Integer:num2
    |Integer:num
    :loop
    <5
    <1
    ?<
    # Id 5 < 1 goto done
    $done

    # Move topmost to another stack
    >num2
    # Add 1 to another stack
    <num2:1
    # Sum them up
    +
    # Push back to origin stack
    <
    $loop

    :done
    .num2

## Methods

Bizarre does not like spaghetti code.
Using only gotos make procedural and
methods quite hard to implement.

We have real method command `@` is here to save.
Methods need to end at double def `@@`, following by optional return stack

    @sumPlusOne:mystack
    <1
    +mystack
    @@mystack

    |Integer:num
    <1
    <2
    <3
    <4
    |Integer:num2
    <10
    <5
    |Integer:res
    $sumPlusOne:num2>res
    <res
    $sumPlusOne:num>res
    <res

Syntax is: `@` followed by method name, then optional parameters separated by colons.
Return is just `@@`.

Call syntax is same as goto `$`, and parameter stacks are defined with colons.
Return stack from call is defined after `>`.

    @sumStacks:stack1:stack2
    |stack1
    <<stack2
    +stack1
    @@stack1

    |Integer:num
    <11
    <5
    |Integer:num2
    <4
    <2
    |Integer:res
    $sumStacks:num2:num>res
    <res

Stacks are passed to methods by VALUE and not by reference,
so every method call will make COPY of the stack.
Return value will be copy of local stack.

## Casting

Since all types are strong, casting is needed for all type conversions.
Programmer should know what is doing, since cast may fail.
Since the best casting is from Britain, our casting symbol is `£`.
Destination stack need to follow the symbol.
Thus we have source and dest types. May cause error to error stack.

    |Unicode:res
    |Integer:num
    <42
    £res
    .res

One is allowed to define source stack as well, but then those two stacks
needs to be separated with colon `:`, while first is source
and second is destination stack. Thus this example outputs `42` even active stack is `num2`.

    |Unicode:res
    |Integer:num
    |Integer:num2
    <num1:42
    <12
    £num1:res
    .res

## Stack size

Sometime you just need to know the size of the stack.
Syntax is `~` followed by target stack or source and target stacks separated by colon `:`.

    |Integer:stacksize
    |Integer:stacksize2
    |Integer:num
    <5<10<9<2<6<1
    ~stacksize
    ~stacksize:stacksize2

On this example stacksize would be `6`, and stacksize2 `1`.


## Reference

System stacks:

 - Default unnamed stack, unicode type
 - `error` stack for error strings (Unicode)
 - `errorcode` stack for error codes (Integer)
 - `result` stack for Boolean results

Parameters defined as:

 - `s` (output) stack name
 - `i` input stack name
 - `t` stack type
 - `l` label
 - `:` literal colon
 - `d` data
 - `D` array of data until EOL

| Operator | Parameters | Description |
|----------|------------|-------------|
| #        | D          | Comment |
| <        | d          | Push |
| <        | s:d        | Push |
| <<       | D          | Push array of data |
| <<       | s:D        | Push array of data |
| >        | s          | Pop |
| >        | i:s        | Pop |
| >>       | s          | Pop array of data |
| >>       | i:s        | Pop array of data |
| £        | s          | Cast from selected stack to defined stack |
| £        | i:s        | Cast from input stack to defined stack |
| ~        | s          | Size of default stack to defined stack |
| ~        | i:s        | Size of defined stack to output stack |
| &#124;   |            | Select default stack |
| &#124;   | t:s        | Define new stack, or empty it |
| &#124;   | s          | Select stack |
| +        | s          | Sum or concatenate all entries in stack |
| -        | s          | Subtract all entries in stack from first, or negate if only one entry |
| *        | s          | Multiply all entries in stack |
| /        | s          | Divide first entry in stack by rest, if only one item it's error |
| %        | s          | Divide first entry in stack by rest, take modulus. If only one item it's error |
| ^        | s          | First item to power of all, ie. first^second^third^...^N |
| 0&       | s          | First item with binary and for rest |
| 0|       | s          | First item with binary or for rest |
| 0^       | s          | First item with binary xor for rest |
| 0~       | s          | Binary negate for all |
| 0!       | s          | Binary not for all |
| _        | s          | Duplicate topmost item in stack |
| .        |            | Write whole stack to stdout |
| .        | s          | Write whole stack to stdout |
| ,        |            | Input from stdin to stack |
| ,        | s          | Input from stdin to stack |
| ?        | s          | Checks if stack is empty |
| ?<       | s          | top-1 < top |
| ?<=      | s          | top-1 <= top |
| ?>       | s          | top-1 > top |
| ?>=      | s          | top-1 >= top |
| ?=       | s          | top-1 == top |
| ?!       | s          | top-1 != top |
| ?0       | s          | top == 0 |
| ?-       | s          | top < 0  |
| :        | l          | Define label |
| $        | l          | Goto label, call method |
| $        | l:s        | Goto label, call method with stack param |
| $        | l:s>i      | Goto label, call method with stack param, and return stack
| @        | l          | Method def |
| @        | l:s        | Method def |
| @@       |            | Return from method |
| @@       | s          | Return from method, return stack |
