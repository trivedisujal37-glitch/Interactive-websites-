

n-int(input("enter the number"))
#hello
#hii
# sujal
li=[]
for i in range(n):
    k=int(input("enter the number"))
    li.append(k)
print("your enterd number are:"li)
re=0
match ch:
    case 1:
        for i in li:
            re+=i
        print("sum is:",re)
    case 2:
        re=li.pop(0)
        for i in li:
            re-=i
        print("product is:",re)

    case 3:
            re=1
            for i in li:
                re*=i
            print("product is:",re)
    case 4:
            re=li.pop(0)
            for i in li:
                re/=i
            print("product is:",re)
        
        
    