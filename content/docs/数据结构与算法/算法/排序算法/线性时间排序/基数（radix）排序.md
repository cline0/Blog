---
title: "基数（radix）排序"
weight: 2
---

动画演示： [https://www.runoob.com/wp-content/uploads/2019/03/radixSort.gif](https://www.runoob.com/wp-content/uploads/2019/03/radixSort.gif)

## 代码
```rust
fn radix_sort(nums: &mut [i32]) {
    // buckets[1..10] 用于负数， buckets[10..] 用于正数, 0 算作正数。
    // 这也导致了一个问题，就是 bucket[0] 是不会被用到的
    // 每个 bucket 从中存取元素的顺序也是关键的一点：插入元素时，要从后面插入，取元素时，要从前面开始取
    let mut buckets: [VecDeque<i32>; 20] = Default::default();

    let max_length = {
        // 一定要对所有元素的绝对值来找最大值
        let mut max = nums.iter().map(|value| value.abs()).max().unwrap();
        let mut cnt = 0;
        while max > 0 {
            max /= 10;
            cnt += 1;
        }
        cnt
    };

    let mut div = 1;
    for _ in 1..=max_length {
        for &num in nums.iter() {
            let bucket_index = {
                let mut mod_result = (num / div) % 10;
                // 加 10 过后，会导致 -9 变为 1， -8 变为 2，故而越小的元素同样也是在越前面，故而后面从 bucket 中取元素的时候就可以直接不考虑正负的关系
                mod_result += 10;
                mod_result as usize
            };

            buckets[bucket_index].push_back(num);
        }

        let mut index = 0;

        for bucket in buckets.iter_mut() {
            while let Some(value) = bucket.pop_front() {
                nums[index] = value;
                index += 1;
            }
        }

        div *= 10;
    }
}
```

## 核心思路
通过比较数字的每一位来进行排序，所以要找到所有元素的最大位数。

当进行低位比较的时候，并不能导致数组完全有序，只能使低位有序，所以，为了使数组完全有序，从 bucket 中取出数组元素的时候一定要有 FIFO 顺序

