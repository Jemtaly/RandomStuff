tokens = {'+': int.__add__, '-': int.__sub__, '*': int.__mul__, '/': int.__floordiv__, '%': int.__mod__}
def RPN(expression):
    stack = []
    for token in expression.split():
        if token in tokens:
            b = stack.pop()
            a = stack.pop()
            stack.append(tokens[token](a, b))
        else:
            stack.append(int(token))
    return stack.pop()
def main():
    while True:
        try:
            print('=>', RPN(input('>> ')))
        except EOFError:
            break
if __name__ == '__main__':
    main()
