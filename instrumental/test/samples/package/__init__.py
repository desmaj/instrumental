def backwards(string):
    return reversed(string)

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        sys.stdout.write(backwards(sys.argv[1]) + "\n")
