import time
dir='o→↑↓←'
def main():
    n=60
    for i in range(n//2):
        info=list(' '*n)
        info[i]=dir[i//3%5]
        info=''.join(info)
        print(f'\r{info}',end='')
        time.sleep(0.2)

if __name__ == "__main__":
    main()