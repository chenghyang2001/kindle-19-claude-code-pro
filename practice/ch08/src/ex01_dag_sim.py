"""練習 01：週報自動化 DAG 的並行模擬。

把題目中的 A~H 任務用 asyncio 模擬，比較三種排程：
1. 全依序（A→B→C→D→E→F→G→H）
2. parallel() + barrier（A‖B → C‖D → E → F → G → H）
3. pipeline()（A→C 與 B→D 兩條流水線各自往前跑，E 前才 barrier）

為了 demo 不真的等 30 秒，用 TIME_SCALE 把「30 秒」縮成 0.3 秒，
最後再換算回題目的秒數。另附「逐項 pipeline」版本：PR 一抓到就送去摘要。
"""
import asyncio
import sys
import time

TASK_SECONDS = 30          # 題目假設：每個任務 30 秒
TIME_SCALE = 0.01          # 30 秒 → 0.3 秒，避免 demo 跑太久

# 依賴圖：任務 → 前置任務
DEPENDENCIES = {
    "A": [], "B": [],
    "C": ["A"], "D": ["B"],
    "E": ["C", "D"],
    "F": ["E"], "G": ["F"], "H": ["G"],
}


async def run_task(name: str, log: list) -> str:
    """模擬一個耗時 TASK_SECONDS 的任務，並記錄開始／結束時刻。"""
    start = time.perf_counter()
    await asyncio.sleep(TASK_SECONDS * TIME_SCALE)
    log.append((name, start, time.perf_counter()))
    return name


async def parallel(*names: str, log: list) -> list:
    """parallel()：同時啟動，全部完成才返回（gather 本身就是 barrier）。"""
    return await asyncio.gather(*(run_task(n, log) for n in names))


async def schedule_sequential(log: list) -> None:
    for name in "ABCDEFGH":
        await run_task(name, log)


async def schedule_parallel_barrier(log: list) -> None:
    await parallel("A", "B", log=log)      # 第 1 波：兩個資料來源互不相依
    await parallel("C", "D", log=log)      # 第 2 波：但 C 要等 B 也做完（barrier 的代價）
    for name in "EFGH":
        await run_task(name, log)


async def schedule_pipeline(log: list) -> None:
    async def lane(*names: str) -> None:
        for name in names:
            await run_task(name, log)

    # 兩條獨立 lane 各自流動，C 不用等 B；E 前是唯一必要的 barrier
    await asyncio.gather(lane("A", "C"), lane("B", "D"))
    for name in "EFGH":
        await run_task(name, log)


async def schedule_item_pipeline(log: list, pr_count: int = 3, task_count: int = 3) -> None:
    """逐項 pipeline：A 每抓到一筆 PR 就丟進 queue，C 立刻摘要（item = 單一 PR / 單一任務）。

    假設：抓取與處理都按「每筆」計時，每筆 = TASK_SECONDS / 筆數。
    """
    async def producer_consumer(fetch: str, process: str, count: int) -> None:
        queue: asyncio.Queue = asyncio.Queue()
        unit = TASK_SECONDS * TIME_SCALE / count

        async def producer() -> None:
            for i in range(count):
                await asyncio.sleep(unit)
                await queue.put(f"{fetch}{i}")
            await queue.put(None)  # 結束訊號

        async def consumer() -> None:
            while (item := await queue.get()) is not None:
                await asyncio.sleep(unit)
                log.append((f"{process}({item})", 0.0, time.perf_counter()))

        await asyncio.gather(producer(), consumer())

    await asyncio.gather(
        producer_consumer("PR", "C", pr_count),
        producer_consumer("T", "D", task_count),
    )
    for name in "EFGH":
        await run_task(name, log)


def verify_order(log: list) -> None:
    """檢查每個任務都在所有前置任務結束後才開始（違反依賴就拋錯）。"""
    times = {name: (s, e) for name, s, e in log if name in DEPENDENCIES}
    for task, deps in DEPENDENCIES.items():
        if task not in times:
            continue
        for dep in deps:
            if dep in times and times[task][0] < times[dep][1] - 1e-4:
                raise AssertionError(f"{task} 在 {dep} 完成前就開始了")


def measure(label: str, scheduler) -> float:
    log: list = []
    start = time.perf_counter()
    asyncio.run(scheduler(log))
    elapsed = time.perf_counter() - start
    verify_order(log)
    simulated = elapsed / TIME_SCALE
    print(f"{label:<28} 實測 {elapsed:5.2f}s → 換算 {simulated:6.1f}s")
    return simulated


def main() -> None:
    try:
        results = {
            "sequential": measure("全依序", schedule_sequential),
            "barrier": measure("parallel() + barrier", schedule_parallel_barrier),
            "pipeline": measure("pipeline()（lane）", schedule_pipeline),
            "item_pipeline": measure("逐項 pipeline（3 筆）", schedule_item_pipeline),
        }
        # 理論值：依序 8×30=240s；並行關鍵路徑 A→C→E→F→G→H = 6×30=180s
        assert abs(results["sequential"] - 240) < 15, results
        assert abs(results["barrier"] - 180) < 15, results
        assert abs(results["pipeline"] - 180) < 15, results
        assert results["item_pipeline"] < results["pipeline"], results
        saved = results["sequential"] - results["barrier"]
        print(f"\n節省 {saved:.0f}s（{saved / results['sequential']:.0%}）；斷言全部通過")
    except AssertionError as err:
        print(f"驗證失敗：{err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
