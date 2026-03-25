---
title: "信息的表示和处理"
type: "docs"
weight: 190
markmap: true
xmindSource: "信息的表示和处理.xmind"
---

```markmap
---
markmap:
  initialExpandLevel: 2
  spacingVertical: 30
  spacingHorizontal: 180
---

# 信息的表示和处理-
- 整数
  - 数字表示
    - 补码
      - 补码的定义 ![补码的定义](images/48b3ec351dc0c7f802aacdcee880cf1552dd9f9fdb6978cf5ee8673b435fe6ed.png)
      - 例如： ![例如：](images/c8d934bbab18bef7f51b113f8b7638790fb7f9458c421cd7ae975a0b2a998b8f.png)
      - 补码的最值
        - 最小值：-2^(w- 1)
        - 最大值：2^(w-1) -1
    - 反码
      - 定义 ![定义](images/690e34a488dc6266c1a1cc3497911ee85697fbaa5dfc2d58587104d56303e196.png)
    - 原码
      - 定义 ![定义](images/7a8b57607ca9f5fce0338272ff67f5a1df55eaeca51c11fc3450a91b2b98cbd9.png)
    - C 语言中的隐式转换
      - 有符号与无符号运算
        - 有符号 -&gt; 无符号
        - ![d909cdf3a50dffc31f13365c16224755dc664622f0ba5ee76e863d8e72502d34.png](images/d909cdf3a50dffc31f13365c16224755dc664622f0ba5ee76e863d8e72502d34.png)
    - 扩展一个数字的位表示
      - 无符号数
        - ![366310b42a504e4de66f25d61d2434f103756d680fd39976cddffa9397e7dc2c.png](images/366310b42a504e4de66f25d61d2434f103756d680fd39976cddffa9397e7dc2c.png)
      - 补码数
        - ![d2682c7f1ecbaa160df1c9b0cc8408442171fef852e185ef64d72c7ae326e57f.png](images/d2682c7f1ecbaa160df1c9b0cc8408442171fef852e185ef64d72c7ae326e57f.png)
    - 截断数字
      - 无符号数
        - ![0d129062fb72542f3a7ae6cac64bd357b0db5d8c684440737afdcf59caaf7d07.png](images/0d129062fb72542f3a7ae6cac64bd357b0db5d8c684440737afdcf59caaf7d07.png)
      - 补码数
        - ![9d5188c41761bf48ff4d2440b2da254609853d289271cb6bdda9aa7b172a23d0.png](images/9d5188c41761bf48ff4d2440b2da254609853d289271cb6bdda9aa7b172a23d0.png)
  - 整数运算
    - 无符号数加法
      - ![f40dffb4406528db6ba381a2f49456578107d008925e6cf870a7a6ea52ce4b3a.png](images/f40dffb4406528db6ba381a2f49456578107d008925e6cf870a7a6ea52ce4b3a.png)
      - 检测溢出： ![检测溢出：](images/40ce92108bc8c912ea94afbaec733e0989246f8f900ff018235e11f3ce258aa0.png)
    - 补码加法
      - ![309cfef1593f43cbc84cfffd28fe6d698334d3b5816d13129d7912e628bc4a5f.png](images/309cfef1593f43cbc84cfffd28fe6d698334d3b5816d13129d7912e628bc4a5f.png)
      - ![2a790b9bb841477991358600a918018360b87a74a280d0f0c3fcf43fe7e2af1b.png](images/2a790b9bb841477991358600a918018360b87a74a280d0f0c3fcf43fe7e2af1b.png)
      - 检测溢出 ![检测溢出](images/e34f1db157f3a5c457c170701544563e64e978cceb7bf027782d0b2e4ab80ee6.png)
    - 补码的非（负）
      - ![809b511de0f642d029bf9d04e3da96a59c2ff97a22d7882769433ecf25331253.png](images/809b511de0f642d029bf9d04e3da96a59c2ff97a22d7882769433ecf25331253.png)
      - 推导： ![推导：](images/cfa4e8301ad68a8106f17504a8c38783fc14a505dc4ec49b4f24d435ce9533ba.png)
      - 位级表示
        - 方法一：每位求反之后再加一 ![方法一：每位求反之后再加一](images/1da983e34138251e59b011fb86bb3305af99f48dc9dc87721422200da0c7386c.png)
        - 方法二： ![方法二：](images/6e34325e282aa899bd314410871daddb7dcbdf651d606d64ff260f2a7cbee6cd.png)
    - 无符号乘法
      - ![1cba653cfb58ae49c5d8609adfa724b72b941f1f616b3d21f367779cbb9cac63.png](images/1cba653cfb58ae49c5d8609adfa724b72b941f1f616b3d21f367779cbb9cac63.png)
    - 补码乘法
      - ![fd54217fdc642759c637b5655ece633c105a6c36f2ed84f5981a16b58a57d052.png](images/fd54217fdc642759c637b5655ece633c105a6c36f2ed84f5981a16b58a57d052.png)
    - 乘以常数
      - 因为计算机执行乘法比较慢，所以，编译器使用移位和加法的组合来代替常数因子因子的乘法
        - ![c7e31f8eb2b37a7d4643c28e965573d8bdfab86ff5fbe33a299cb8c66127f08f.png](images/c7e31f8eb2b37a7d4643c28e965573d8bdfab86ff5fbe33a299cb8c66127f08f.png)
        - ![aff9b6bbfa03bf892301ffaf9e55f2a816a24fad6617a28304ebd0a4fbd1a6d9.png](images/aff9b6bbfa03bf892301ffaf9e55f2a816a24fad6617a28304ebd0a4fbd1a6d9.png)
        - ![4e3e98210d9856be134e808e16aef2a67ed2e1136d87b6babe1b621e42b09c20.png](images/4e3e98210d9856be134e808e16aef2a67ed2e1136d87b6babe1b621e42b09c20.png)
        - 例如，x * 14，其中 14 = 2^3 + 2^2 + 2^1，所以，编译器将乘法重写为 (x&lt;&lt;3) + (x&lt;&lt;2) + (x&lt;&lt;1)
    - 除以2的幂
      - 无符号 ![无符号](images/73d7ab50f017d56f29eb3c37fa374bec4e6715878d2853e6a8279ce77781550b.png)
      - 补码，向下舍入（-771.25 会舍入为 -772) ![补码，向下舍入（-771.25 会舍入为 -772)](images/a769498838f5d0ff4f9f85d4059c0c51e12f6243d33d25d54bd8808551f8bac8.png)
      - 补码，向上舍入（-771.25 会舍入为 -771） ![补码，向上舍入（-771.25 会舍入为 -771）](images/ae0f5adee77457d4707fdd738687cee9501debed0ba9bda1a2ab3bc093390c9e.png)
        - 原理 ![原理](images/1eaeeac2917236fe7f2e6eeb7aad531f1ed436e7c63fcf41a053e2e0ecb17414.png)
- 浮点数
  - 二进制小数
    - 数字表示
      - 定义： ![定义：](images/2c5a1af6e4085a828473f2dd92d82e39e68d48b2b9435d384d2140c24a495178.png)
      - 二进制小数点向左移动一位相当于这个数被 2 除。
      - 类似，二进制小数点向右移动一位相当于将该 数乘 2
      - ![4181e2507312aa5c9eecb602cd7050b820fb26559ea63a70b86c4271a4f54b93.png](images/4181e2507312aa5c9eecb602cd7050b820fb26559ea63a70b86c4271a4f54b93.png)
  - IEEE浮点表示
    - ![4a73717162c9d73c609aaceaa6f9a5ba54f1168c3f239caba14160ad23fec565.png](images/4a73717162c9d73c609aaceaa6f9a5ba54f1168c3f239caba14160ad23fec565.png)
    - ![743357c4f478e49410370142bd6210e1dadf1a24a9b00274f2a9d4a9555961e2.png](images/743357c4f478e49410370142bd6210e1dadf1a24a9b00274f2a9d4a9555961e2.png)
    - 单精度：s = 1, k = 8, n = 23 双精度：s = 1, k = 11, n = 52 ![单精度：s = 1, k = 8, n = 23 双精度：s = 1, k = 11, n = 52](images/3185e9fa4da7a0b22cc90e594a5ab1337873a107a63949872ae456a15fac0ef2.png)
    - 根据 exp 的值，被编码值可以分为 3 中不同的情况（最后一种有两种变体）
      - 规格化的， exp != 0 && exp != 255 ![规格化的， exp != 0 && exp != 255](images/d26ee1d32dfcf2a6a3f69ca01556c554918f141973a604b66f2f2e4700bdca8a.png)
        - 阶码字段被解释为以偏置(biased)形式表示的有符号整数，阶码的值 E=e-Bias，e 是无符号数即 exp 表示的值，Bias = 2^(k - 1) - 1。 Bias = 127 (单精度） Bias = 1023 （双精度）
        - 小数字段 frac 被解释为描述小数值 f（无符号值），其中 0 &lt;= f &lt; 1，尾数定义为 M = 1 + f，因此我们可以把 M 看成一个二进制表达式为1.xxxx的数字
      - 非规格化的，e = 0 ![非规格化的，e = 0](images/1e40faed4b1af11bf7ede0dbf8484adf1669f178d06084ffeacb4d1182e1c146.png)
        - 此时，E = 1 - Bias, M = f
        - 0 是非规格化数（f = 0)
        - 接近 0 的数也是非规格化的 这是 k = 3, n = 2时能表示的数： ![接近 0 的数也是非规格化的 这是 k = 3, n = 2时能表示的数：](images/8a7bd3f730eaab4a014c2b20b29e5480d5a0327d0bc7092382b51bac944d056c.png)
      - 无穷大 ![无穷大](images/abcb944a6648df44ec3dbf67eac1241d6a2ae3f6f85cc5dc5cd30f2b09250d44.png)
      - NaN ![NaN](images/6e187c29628179f6227a3133784be11bcc94a9569852c859fbd319913f48ea17.png)
    - 一些规律
  - 舍入
    - 对于值 x,我们一般想用 一 种系统的方法，能够找到“最接近的匹配值 x' 可以用期望的浮点形式表示出来。这就是舍入 (rounding) 运算的任务
    - 四种舍入方式
      - 向偶数舍入（round to even） 也称向最接近的值舍入（round to nearest） 这是默认的方式
        - 它将数字向上或者向下舍入，使得结果的最低有效数字是偶数。
        - 这种方法将 1.5 美元和 2. 5 美元都舍入成 2 美元。
      - 向零舍入
        - 向零舍入方式把正数向下舍入，把负数向上舍入得到的值 x'， 是得 |x'| &lt;= |x|
      - 向下舍入
        - 向下舍入方式把正数和负数都向下舍入,得到 x', 使得 x' &lt;= x
      - 向上舍入
        - 向上舍入方式把正数和负数都向上舍入，得到 x'，使得 x &lt;= x'
      - 例子 ![例子](images/df126bb27d887f754c528b3571ce8504b86ee9074d8a8f85404fdc392865c05e.png)
      - 由于舍入导致的问题
        - 加法
          - 加法可交换 ![加法可交换](images/e64788e06f4e6855b884d2e08b028d3940d798da7b00d4499eb738084424998f.png)
          - 加法不可结合 例如，使用单精度浮点，表达式(3. 14+le10) -le10 求值得到0.0。因为舍入，值 3. 14 会丢失。
          - 无穷有关的计算 ![无穷有关的计算](images/2c42389c7b50a6d2083b9e2e057b4ce613a8452cb0eb5c892532bd804781db8d.png)
          - 满足了单调性 ![满足了单调性](images/3becc807bbe4a7c24ab179f9a395703f20f114aae79a599486e09c6ddaf8f3b9.png)
        - 乘法
          - 不具备可结合性
          - 不可分配性
          - 满足下列单调性： ![满足下列单调性：](images/9b4449829381a04d12c1b7f868e19ae98d8f77a2a10f1b61380bdcb144715fa5.png)
  - C 语言中的 int, float, double 进行强制类型转换
    - ![8bccc428bc0655e3f6a40ed19c798db9b104b96e483d418e3db0ab53a849ce9c.png](images/8bccc428bc0655e3f6a40ed19c798db9b104b96e483d418e3db0ab53a849ce9c.png)
```
