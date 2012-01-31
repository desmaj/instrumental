def backwards(string):
    return reversed(string)

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        print backwards(sys.argv[1])
