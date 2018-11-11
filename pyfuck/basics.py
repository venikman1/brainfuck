class BF_shell:
    def __init__(self, code_stream, memory_size = 1000):
        self.memory_size = memory_size
        self.free = [True] * memory_size
        self.pointer = 0
        self.code_stream = code_stream
        self.moved = None

    def dump(self):
        self.code_stream.add('#')

    def find_mem(self, size = 1):
        for i in range(0, len(self.free) - size + 1):
            if all(self.free[i:i + size]):
                self.free[i:i + size] = [False] * size
                return i
        return False

    def free_mem(self, i, size = 1):
        self.free[i: i + size] = [True] * size

    def goto(self, pointer):
        if self.moved:
            self.moved.backward()
            self.moved = None
        if isinstance(pointer, BF_reverse_buffer):
            rel = pointer.pointer - self.pointer
            if rel > 0:
                res = '>' * rel
            else:
                res = '<' * -rel
            self.pointer = pointer.pointer
            self.code_stream.add(res)
            pointer.forward()
            self.moved = pointer
        else:
            rel = pointer - self.pointer
            if rel > 0:
                res = '>' * rel
            else:
                res = '<' * -rel
            self.pointer = pointer
            self.code_stream.add(res)

    def zero(self, *targets):
        for i in targets:
            self.goto(i)
            self.code_stream.add('[-]')

    def move(self, source, *targets):
        self.goto(source)
        self.code_stream.add('[')
        for i in targets:
            self.goto(i)
            self.code_stream.add('+')
        self.goto(source)
        self.code_stream.add('-]')

    def move_invert(self, source, *targets):
        self.goto(source)
        self.code_stream.add('[')
        for i in targets:
            self.goto(i)
            self.code_stream.add('-')
        self.goto(source)
        self.code_stream.add('-]')


    def copy(self, source, *targets):
        temp = self.find_mem()
        self.zero(*targets, temp)
        self.move(source, *targets, temp)
        self.move(temp, source)
        self.free_mem(temp)

    def inc(self, target, n):
        self.goto(target)
        self.code_stream.add((lambda x: '+' if n > 0 else '-')(n) * abs(n))

    def set(self, target, n):
        self.goto(target)
        self.zero(target)
        self.inc(target, n)

    def raw_print(self, target):
        self.goto(target)
        self.code_stream.add('.')

    def raw_scan(self, target):
        self.goto(target)
        self.code_stream.add(',')

    def add(self, target, source):
        temp = self.find_mem()
        self.copy(source, temp)
        self.move(temp, target)
        self.free_mem(temp)


    def sub(self, target, source):
        temp = self.find_mem()
        self.copy(source, temp)
        self.move_invert(temp, target)
        self.free_mem(temp)

    def if_func(self, condition, *body):
        condition_copy = self.find_mem()
        self.copy(condition, condition_copy)
        self.goto(condition_copy)
        self.code_stream.add("[")
        for b in body:
            b()
        self.goto(condition_copy)
        self.zero(condition_copy)
        self.code_stream.add("]")
        self.free_mem(condition_copy)

    def while_func(self, condition, *body):
        self.goto(condition)
        self.code_stream.add("[")
        for b in body:
            b()
        self.goto(condition)
        self.code_stream.add("]")

    def condition_not_eq(self, a, b):
        temp = self.find_mem()
        self.copy(a, temp)
        self.sub(temp, b)
        return temp

    def condition_neg(self, a):
        temp = self.find_mem()
        self.zero(temp)
        counter = self.find_mem()
        self.set(counter, 128)
        copied = self.find_mem()
        self.copy(a, copied)
        inv = self.find_mem()
        def body():
            self.inc(counter, -1)
            self.inc(copied, 1)
            self.copy(copied, inv)
            self.invert_condition(inv)
            self.if_func(inv, lambda : self.set(temp, 1))
        self.while_func(counter, body)

        self.free_mem(counter)
        self.free_mem(copied)
        self.free_mem(inv)
        return temp

    def invert_condition(self, condition):
        #self.code_stream.add('#')#
        temp = self.find_mem()
        self.set(temp, 1)
        self.if_func(condition, lambda : self.zero(temp))
        self.copy(temp, condition)
        self.free_mem(temp)
        #self.code_stream.add('#')#

    def print_text(self, text):
        temp = self.find_mem()
        for c in text:
            self.set(temp, ord(c))
            self.raw_print(temp)
        self.free_mem(temp)

    def move_with_carry(self, source, carry, *targets):
        condition = self.find_mem()
        self.goto(source)
        self.code_stream.add('[')
        for i in targets:
            self.goto(i)
            self.code_stream.add('+')
            #CARRY
            self.copy(i, condition)
            self.invert_condition(condition)
            self.if_func(condition, lambda : self.inc(carry, 1))
        self.goto(source)
        self.code_stream.add('-]')
        self.free_mem(condition)

    def move_invert_with_carry(self, source, carry, *targets):
        condition = self.find_mem()
        self.goto(source)
        self.code_stream.add('[')
        for i in targets:
            self.copy(i, condition)
            self.invert_condition(condition)
            self.if_func(condition, lambda: self.inc(carry, 1))
            self.goto(i)
            self.code_stream.add('-')
        self.goto(source)
        self.code_stream.add('-]')
        self.free_mem(condition)

    def add_with_carry(self, target, source, carry):
        temp = self.find_mem()
        self.copy(source, temp)
        self.move_with_carry(temp, carry, target)
        self.free_mem(temp)

    def sub_with_carry(self, target, source, carry):
        temp = self.find_mem()
        self.copy(source, temp)
        self.move_invert_with_carry(temp, carry, target)
        self.free_mem(temp)

    def mult(self, target, source, carry):
        adder = self.find_mem()
        rep = self.find_mem()
        self.copy(source, rep)
        self.zero(adder)
        self.move(target, adder)

        self.goto(rep)
        self.code_stream.add('[')

        self.add_with_carry(target, adder, carry)

        self.goto(rep)
        self.code_stream.add('-]')

        self.free_mem(adder)
        self.free_mem(rep)

    def div(self, target, source, result):
        """

        :param target: остаток
        :param source: делитель
        :param result: целочисленное деление
        :return:
        """
        condition = self.find_mem()
        self.set(condition, 255)
        def while_body():
            self.sub_with_carry(target, source, condition)
            self.inc(result, 1)
        self.while_func(condition, while_body)

        self.add(target, source)
        self.inc(result, -1)

        self.free_mem(condition)

    def div_long(self, target, target_high, source, result):
        """

        :param target: остаток
        :param source: делитель
        :param result: целочисленное деление
        :return:
        """
        condition = self.find_mem()
        carry = self.find_mem()
        self.set(condition, 255)
        self.zero(carry)
        def while_body():
            self.sub_with_carry(target, source, carry)
            self.move_invert_with_carry(carry, condition, target_high)
            self.inc(result, 1)
        self.while_func(condition, while_body)

        self.add(target, source)
        self.inc(result, -1)
        self.inc(target_high, 1)
        self.free_mem(condition)
        self.free_mem(carry)



class BF_integer:
    def __init__(self, shell, size=4):
        self.shell = shell
        self.pointer = self.shell.find_mem(size=size)
        self.size = size

    def set(self, value):
        for i in range(self.pointer, self.pointer + self.size):
            self.shell.set(i, value % 256)
            value //= 256

    def add(self, other):
        carry1 = self.shell.find_mem()
        carry2 = self.shell.find_mem()
        self.shell.zero(carry1)
        self.shell.zero(carry2)
        for i in range(self.size):
            self.shell.add_with_carry(self.pointer + i, other.pointer + i, carry2)
            self.shell.move_with_carry(carry1, carry2, self.pointer + i)
            carry1, carry2 = carry2, carry1
        self.shell.free_mem(carry1)
        self.shell.free_mem(carry2)

    def sub(self, other):
        carry1 = self.shell.find_mem()
        carry2 = self.shell.find_mem()
        self.shell.zero(carry1)
        self.shell.zero(carry2)
        for i in range(self.size):
            self.shell.sub_with_carry(self.pointer + i, other.pointer + i, carry2)
            self.shell.move_invert_with_carry(carry1, carry2, self.pointer + i)
            carry1, carry2 = carry2, carry1
        self.shell.free_mem(carry1)
        self.shell.free_mem(carry2)

    def copy(self, other):
        for i in range(self.size):
            self.shell.copy(other.pointer + i, self.pointer + i)

    def zero(self):
        for i in range(self.size):
            self.shell.zero(self.pointer + i)

    def mult(self, other):
        temp = BF_integer(self.shell, size=self.size)
        temp.zero()
        for i in range(self.size):
            self.shell.mult(self.pointer + i, other, temp.pointer + ((i + 1) % temp.size))
            # self.shell.goto(temp.pointer + ((i + 1) % temp.size))
            # self.shell.dump()
        self.shell.zero(temp.pointer)
        self.add(temp)
        del temp

    def div(self, other, carry):
        res = self.shell.find_mem()
        self.shell.zero(carry)
        self.shell.zero(res)
        for i in range(self.size - 1, -1, -1):
            self.shell.div_long(self.pointer + i, carry, other, res)
            self.shell.move(self.pointer + i, carry)
            self.shell.move(res, self.pointer + i)

        self.shell.free_mem(res)

    def condition_not_null(self):
        res = self.shell.find_mem()
        self.shell.zero(res)
        for i in range(self.size):
            self.shell.if_func(self.pointer + i, lambda : self.shell.inc(res, 1))
        return res

    def condition_neg(self):
        return self.shell.condition_neg(self.pointer + self.size - 1)

    def condition_less(self, other):
        tmp = BF_integer(self.shell, size=self.size)
        tmp.copy(self)
        tmp.sub(other)
        res = tmp.condition_neg()
        del tmp
        return res

    def scan(self):
        self.zero()
        inp = BF_integer(self.shell, size=self.size)
        inp.zero()
        ten = self.shell.find_mem()
        self.shell.set(ten, 10)
        self.shell.raw_scan(inp.pointer)
        self.shell.inc(inp.pointer, -ord(' '))
        def while_body():
            self.shell.inc(inp.pointer, ord(' ') - ord('0'))
            self.mult(ten)
            self.add(inp)
            self.shell.raw_scan(inp.pointer)
            self.shell.inc(inp.pointer, -ord(' '))
        self.shell.while_func(inp.pointer, while_body)

        self.shell.free_mem(ten)
        del inp

    def print(self):
        ten = self.shell.find_mem()
        self.shell.set(ten, 10)
        mod = self.shell.find_mem()
        condition = self.shell.find_mem()

        self.shell.set(condition, 1)

        buffer = BF_reverse_buffer(self.shell)
        buffer.zero()
        printed = BF_integer(self.shell, size=self.size)
        printed.copy(self)

        def while_body():
            printed.div(ten, mod)
            self.shell.inc(mod, ord('0'))
            #self.shell.raw_print(mod)
            self.shell.copy(mod, buffer)
            buffer.push()
            #END
            cond = printed.condition_not_null()
            self.shell.copy(cond, condition)
            self.shell.free_mem(cond)
        self.shell.while_func(condition, while_body)

        buffer.print()

        self.shell.free_mem(ten)
        self.shell.free_mem(condition)
        self.shell.free_mem(mod)
        del buffer
        del printed

    def __del__(self):
        self.shell.free_mem(self.pointer, self.size)

class BF_mem_mover:
    def forward(self):
        pass

    def backward(self):
        pass

class BF_reverse_buffer(BF_mem_mover):
    def __init__(self, shell = BF_shell, size=120):
        self.shell = shell
        self.pointer = self.shell.find_mem(size=size)
        self.size = size

    def zero(self):
        for i in range(self.size):
            self.shell.zero(self.pointer + i)

    def forward(self):
        self.shell.code_stream.add('>>[>>]<')

    def backward(self):
        self.shell.code_stream.add('<[<<]')

    def push(self):
        self.shell.goto(self)
        self.shell.code_stream.add('>+>')

    def print(self):
        self.shell.goto(self)
        self.shell.code_stream.add('<[<.><<]')
        self.forward()

    def __del__(self):
        self.shell.free_mem(self.pointer, size=self.size)

from code_stream import code_stream
cs = code_stream()

shell = BF_shell(cs)
# a = shell.find_mem()
# b = shell.find_mem()
# shell.raw_scan(a)
# shell.raw_scan(b)
# cond = shell.condition_not_eq(a, b)
# shell.if_func(cond, lambda :shell.print_text("NOT EQUAL"))
# shell.invert_condition(cond)
# shell.if_func(cond, lambda :shell.print_text("EQUAL"))

# a = BF_integer(shell)
# b = shell.find_mem()
# mod = shell.find_mem()
# shell.set(b, 10)
# a.set(999)
# a.div(b, mod)

# a = shell.find_mem()
# b = shell.find_mem()
# c = shell.find_mem()
# trash = shell.find_mem()
# shell.set(a, 34)
# shell.set(b, 1)
# shell.set(c, 16)
# shell.div_long(a, b, c, trash)

a = BF_integer(shell, size=16)
a.scan()
b = BF_integer(shell, size=16)
b.scan()
c = BF_integer(shell, size=16)

condition = shell.find_mem()
shell.set(condition, 1)

def while_body():
    cond = a.condition_less(b)
    def swap():
        c.copy(a)
        a.copy(b)
        b.copy(c)
    shell.if_func(cond, swap)
    a.sub(b)
    shell.free_mem(cond)
    cond = a.condition_not_null()
    shell.copy(cond, condition)
    shell.free_mem(cond)
shell.while_func(condition, while_body)
b.print()

# a = shell.find_mem()
# shell.set(a, 65)
# buffer = BF_reverse_buffer(shell)
# shell.copy(a, buffer)
# buffer.push()
# shell.inc(buffer, 23)
print(len(str(cs)))

with open("../interpreter/code.bf", "w") as f:
    f.write(str(cs))
print(cs)
