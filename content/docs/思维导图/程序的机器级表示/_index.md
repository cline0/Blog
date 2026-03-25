---
title: "程序的机器级表示"
type: "docs"
weight: 270
markmap: true
xmindSource: "程序的机器级表示.xmind"
---

```markmap
---
markmap:
  initialExpandLevel: 2
  spacingVertical: 30
  spacingHorizontal: 180
---

# 程序的机器级表示
- X86-64
  - 整数寄存器
    - ![fcb872e141386096b0be727ebcc7b5a2d49d119df4dd79ac650b2119d16ae21c.png](images/fcb872e141386096b0be727ebcc7b5a2d49d119df4dd79ac650b2119d16ae21c.png)
- 访问信息
  - 操作数指示符
    - 操作数格式 ![操作数格式](images/795ac90db59815b55ff6b418c11d595f11668e5c6a571af50f900fdaa29e48fb.png)
  - 数据传送指令
    - 简单的数据传送指令 ![简单的数据传送指令](images/4ed0a392a6d6ff324223c418497d499b58684358130fb38a54b77e1c8e0b7e62.png)
      - 五种可能的组合 ![五种可能的组合](images/51973c1ba07473f87b1c8a0c247824ee408cc79f416286f5cd3d255c59c96e07.png)
      - movl 指令会将 64 位寄存器的高 32 位置为 0
      - movq 指令只能适用于 32 位立即补码数，会进行符号扩展。 movabsq 适用于 64 位立即数
    - 零扩展数据传送指令 ![零扩展数据传送指令](images/793a45476cf5668c82409ae6e68c151d16e144bcbc3c3d35feee76e1f2f93a7e.png)
    - 符号扩展数据传送指令 ![符号扩展数据传送指令](images/f2fb978976065f2fcebfbed2557e2c260094bdfb8ffd52b1f31950dc44b84187.png)
    - 压入和弹出栈数据 ![压入和弹出栈数据](images/59e548cee06069a567c2a08ad429e386fc6e737f345e92b6a14ef89add80de27.png)
      - 栈向下增长，栈顶元素的地址是所有栈中元素地址最低的
  - 算术和逻辑操作
    - 整数算术操作 ![整数算术操作](images/e7d8218ea1ebbde8bcd1ce6576e2edde5a37f8f50352a805c93f6f88764ea912.png)
      - 加载有效地址(load effective address） leaq指令
        - 该指令并不是从指定的位置读入数据，而是将有效地址写人到目的操作数。
        - 一种用法是为后面的内存引用产生指针 ![一种用法是为后面的内存引用产生指针](images/e646daffac1ce5c800ca5452d8e501a93035d9825ce47613ea1a23e5e425ac0e.png)
        - 另一种用法是简洁地描述普通的算术操作
          - ![e6e7b0a640552e9230096db602810fcf4af8534da778c87b2e0f0075021fb84b.png](images/e6e7b0a640552e9230096db602810fcf4af8534da778c87b2e0f0075021fb84b.png)
          - ![fca368daec6e4f7c9c134de7721c82431ac027753d984e6803f0045a0aec8110.png](images/fca368daec6e4f7c9c134de7721c82431ac027753d984e6803f0045a0aec8110.png)
    - 特殊的算术操作 ![特殊的算术操作](images/c1ec9703c3a1dc6df06adafea5c5355044e541158694d2a33fe47bec940afe7e.png)
      - clto 指令的 o 指的是八字(oct word）
- 控制
  - 条件码
    - 标志寄存器（条件码（condition code）寄存器）
      - 常用条件码 ![常用条件码](images/4475a8bd06059de52da4445b67bfb899bee57d89c10138bf3ba83c47a901a918.png)
    - 指令对条件码的影响
      - 逻辑操作：如 XOR，进位标志和溢出标志置为 0
      - 移位操作：进位标志将设置为最后一个被操作的位，溢出标志设置为 0
      - INC 和 DEC 指令会设置溢出和零标志，但是不会改变进位标志
      - 比较和测试指令 ![比较和测试指令](images/7bbfcb64966e70315b278cf15e804024c6a46703b637bf3c1b3caad2c6953ab0.png)
    - 访问条件码
      - 根据条件码的某种组合，将一个字节设置为 0 或者 1
        - SET 指令，其目的操作数是低位单字节寄存器，或者是一个字节的内存位置 ![SET 指令，其目的操作数是低位单字节寄存器，或者是一个字节的内存位置](images/61c77a9277187134bc2c60f5f7db36054d000424009422745eab0cf64e86fac6.png)
          - 例如： ![例如：](images/35d1505c06c204f12cc4333d1e5b2ee6f064c64f5c21088f4a92e63d941ea962.png)
      - 条件跳转到程序的某个其他部分
        - 跳转指令 ![跳转指令](images/e2a73c165c08c7cd6bde911787a3c0727dc7cf841fddd25a7c00268508d3185d.png)
          - 间接跳转示例： jmp *%rax //rax 中值作为跳转目标 jmp *(%rax) //rax中的值作为读地址，从内存中读出跳转目标
      - 条件传送数据
        - 条件传送指令 ![条件传送指令](images/0ef8acbacf6b0c4a9cafeda03fc837c70e9e4807051cb047bd6fa61740c22c68.png)
  - 循环
    - do-while 循环
      - ![b92926b2e69bb667e65859c36b4fc2b0ba33878cedcfe3add27c3d9f286a82ec.png](images/b92926b2e69bb667e65859c36b4fc2b0ba33878cedcfe3add27c3d9f286a82ec.png)
    - while 循环
      - jump to middle ，-Og 选项时对应的汇编代码 ![jump to middle ，-Og 选项时对应的汇编代码](images/557ffbe8c7ead49eaa9f90fd843b26bdf020f043c83bb97ab4f5a1b33a98dbe4.png)
      - guarded-do, -O1 选项 ![guarded-do, -O1 选项](images/d6bf9fcbbf0cd2e6f37b831426d396163baa3526f12dfe08b9acb048c8e1f680.png)
    - for 循环
      - ![1cb535a0d357a55ea2b42942a84975467f15c29c3c2855aa8e2772a2249a3154.png](images/1cb535a0d357a55ea2b42942a84975467f15c29c3c2855aa8e2772a2249a3154.png)
  - 过程（函数）
    - 通用栈帧结构，其中，参数构造区用来存储传递给下一个过程的参数 ![通用栈帧结构，其中，参数构造区用来存储传递给下一个过程的参数](images/69fbd2c3dbf7f7b75d4426deab2e1b9abc46e44e55991342356d61c763f416af.png)
    - 转移控制
      - call 和 ret 指令的一般形式 ![call 和 ret 指令的一般形式](images/4319b3ac02784093c40bbdd20cc2611257eb2501ef358c94df31e11304d9b4dd.png)
        - 在过程 P 中执行 call Q 指令：将继续 P 的执行的代码位置 A （返回地址） 压入栈中，并将 PC 设置为 Q 的起始地址。 ret 指令从栈中弹出地址 A，并将 PC 设置为 A
    - 数据传送
      - 参数传递
        - 在 X86-64 中，大部分过程间的数据传送都是通过寄存器来实现的。
          - 最多可以通过寄存器传递 6 个整形参数。
          - 寄存器的使用有特殊顺序
          - 传递函数参数的寄存器 ![传递函数参数的寄存器](images/f4cf7a854f0de52470bb1b6c5a42c60f54179bd345042636c1a9dbd4076c413b.png)
        - 大于 6 个整形的参数，超出 6 个的部分通过栈来传递
          - 假设过程 P 调用过程 Q,有 n 个整型参数，且 n &gt; 6 。那么 P 的代码分配的栈帧必须要能容纳 7 到 n号参数的存储空间
    - 栈上的局部存储
      - 局部数据必须存放在内存中的情况
        - 寄存器不足够存放所有的本地数据
        - 对一个局部变量使用地址运算符＇＆＇，因此必须能够为它产生一个地址
        - 某些局部变量是数组或结构，因此必须能够通过数组或结构引用被访问到
      - 变长栈帧
        - alloca 函数可以在栈上分配任意字节数量的存储，当代码声明一个局部变长数组时，就会发生这种情况
    - 寄存器中的局部存储空间
      - 寄存器组是唯一被所有过程共享的资源
      - 被调用者保存寄存器
        - 寄存器 %rbx , %rbp 和 %r12~%r15 被划分为被调用者保存寄存器
        - 当过程 P 调用过程 Q 时，Q 必须保存这些保存寄存器的值，保证他们的值在 Q 返回到 P 时与 Q 被调用时是一样的
        - 所有其他寄存器，除了 %rsp，都是调用者保存寄存器，这意味着任何函数都能修改他们
    - 数组分配与访问
      - 指针的相关运算
        - E 是一个 int 型的数组 ![E 是一个 int 型的数组](images/fb20fe1abce5354a9ddfc657cbdbd623a251c8e24c21cea00cbc925e20d0ecfe.png)
      - 多维数组
        - int A[5][3] 在内存中的布局： ![int A\[5\]\[3\] 在内存中的布局：](images/9df254d4c3a5dd6bfff7d2222692b5919a8f5a1fb29bc14cc9e33cb5325e647f.png)
        - 通常来说，对于一个声明如下的数组： T D[R] [C]; 它的数组元素 D[i][j] 的内存地址为 &D[i][j] = X_D + L * (C * i + j) 这里，L 是数据类型 T 以字节为单位的大小。X_D 是 D 的内存地址
  - 异质的数据结构
    - 结构
      - 结构的所有组成部分都存放在内存中一段连续的区域内
      - 指向结构的指针就是结构第一个字节的地址。
      - 编译器维护关于每个结构类型的信息，指示每个字段的字节偏移，它以这些偏移作为内存引用指令中的位移，从而产生对结构元素的引用
    - 联合
      - 以多种类型来引用一个对象
      - 一个联合的总的大小等于它最大字段的大小
    - 数据对齐
      - 对齐数据可以提高内存系统的性能
      - 对齐的原则是任何 K 字节的基本对象的地址必须是 K 的倍数
  - gdb
    - 常用的命令 ![常用的命令](images/d29c78fa23b0aee1e5219b6353fa2893c2ad11abbacb9b3bee138b4539a137c3.png)
- 浮点代码
  - AVX2 中的 YMM 寄存器
    - 媒体寄存器 ![媒体寄存器](images/8eb4288be3bb286c483394716da003ff4ee1e925adbc909c78f4694372c2b1ad.png)
  - 浮点传送和转换操作
    - 浮点传送指令 ![浮点传送指令](images/077bb9fa76ab642700ce218352ac953883fa9a7bb4069258cac329dbd472fd27.png)
    - 双操作数浮点转换指令，截断（truncation）会把值向零进行舍入 ![双操作数浮点转换指令，截断（truncation）会把值向零进行舍入](images/d0f32b415d3ac1ed6386f4a67418b8f71cf2683c4d59fa935fa91a61ab672fa0.png)
    - 三操作数浮点转换指令，第二个源操作数只会影响结果的高位字节 ![三操作数浮点转换指令，第二个源操作数只会影响结果的高位字节](images/1bceadbae2a7b8fa29e340f625ccf701166b586cc20b8e2063dd63823fc54746.png)
      - 例如： ![例如：](images/4068a1a26648a36b360bd7edace38bf4d925995ff0fe73a1ff6af5faa51e4bcb.png)
    - ![7b026246eb794eddb07791d280e1a94e592e443c5b88e13e0b1a51a9e197a23c.png](images/7b026246eb794eddb07791d280e1a94e592e443c5b88e13e0b1a51a9e197a23c.png)
      - vunpcklps 指令用来交叉放置来自两个 XMM 寄存器的值，把他们存储到第三个寄存器中。
        - ![1ceca7944da84bb43d1dc05f2a698d31b495b374529acd9ce1f219934c488442.png](images/1ceca7944da84bb43d1dc05f2a698d31b495b374529acd9ce1f219934c488442.png)
      - vcvtps2pd 指令把源 XMM 寄存器中的两个低位单精度值扩展成目的 XMM 寄存器中的两个双精度值 。
        - 对 vunpcklps 指令的结果运用这条指令会得到值 [dx_0, dx_0] 这里 dx_0 是将 x 转换成双精度后的结果 。
  - 浮点运算操作
    - 标量浮点算术操作 ![标量浮点算术操作](images/1179909d2f5bad8e2b18c0ad3afd6235606911aea31f6a6a6564cb1c17168917.png)
```
