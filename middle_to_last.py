# -*-encoding:utf-8-*-
#!/usr/bin/python
# create by yuerguang.cl@gmail.com
# Convert Infix expression into Postfix expression


import unittest

# 优先级判断
def prior(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0


def infix_to_postfix(middle):
    '''
        利用list特性来模拟Stack.
        1.当读到一个操作数时，立即将它放到输出中
        2.操作符则不立即输出，放入栈中。遇到左圆括号也推入栈中
        3.如果遇到一个右括号，那么就将栈元素弹出，将符号写出直到遇到一个对应的左括号。但是这个左括号只被弹出，并不输出
        4.在读到操作符时，如果此时栈顶操作符优先性大于或等于此操作符，弹出栈顶操作符直到发现优先级更低的元素位置。除了处理)的时候，否则决不从栈中移走(
        5.如果读到输入的末尾，将栈元素弹出直到该栈变成空栈，将符号写到输出中
        6.操作符中，+-优先级最低,()优先级最高
    :param middle:
    :return:
    '''
    op = []
    ans = ''
    i = 0
    lenth = len(middle)
    while i < lenth:
        c = middle[i]
        if c >= '0' and c <= '9':
            ans += c
        elif c == '(':
            op.append('(')
        elif c == ')':  # 右边的括号遇到开始pop栈，直到遇到左括号
            while op[-1] != '(':
                ans += op[-1]
                op.pop()
            op.pop()
        else:  # 操作符号
            if len(op) == 0:
                op.append(c)
            else:
                if prior(c) > prior(op[-1]):  # 高优先级入栈
                    op.append(c)
                else:
                    while len(op) > 0 and prior(c) <= prior(op[-1]):  # 低优先级出栈
                        ans += op[-1]
                        op.pop()
                    op.append(c)
        i += 1  # 开始遍历下一个字符

    while len(op) > 0:
        ans += op[-1]
        op.pop()
    return ans


# unittest
class mytest(unittest.TestCase):
    # #初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    # 具体的测试用例，以test开头,和java的一样
    def testInfix2Postfix(self):
        self.assertEqual(infix_to_postfix('1+2*3'), '123*+', 'test fail')
        self.assertEqual(infix_to_postfix('(8+9*10)-4/2+3'), '8910*+42/-3+', 'test fail')
        self.assertEqual(infix_to_postfix('1+2*3+(4*5+6)*7'), '123*+45*6+7*+', 'test fail')
        self.assertEqual(infix_to_postfix('1+2-3/4'), '12+34/-', 'test fail')
        self.assertEqual(infix_to_postfix('1+(2*3/4)'), '123*4/+', 'test fail')


if __name__ == '__main__':
    print(infix_to_postfix('1+2*3'))  # 123*+
    print(infix_to_postfix('(8+9*10)-4/2+3'))  # 8910*+42/-3+
    print(infix_to_postfix('1+2-3/4'))  # 8910*+42/-3+
    unittest.main()
