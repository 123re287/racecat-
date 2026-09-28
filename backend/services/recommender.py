def calculate_task_score(priority, difficulty, estimated_minutes, days_left):
    # 越接近截止日期，紧迫程度越高
    if days_left <= 0:
        urgency = 100
    else:
        urgency = 10 / days_left

    # 重要程度越高，分数越高
    importance = priority

    # 难度越高，需要提前准备，因此增加一点权重
    difficulty_weight = 1 + difficulty * 0.1

    # 时间越长，说明任务规模越大，适当增加权重
    time_weight = 1 + estimated_minutes / 600

    score = (
        importance
        * urgency
        * difficulty_weight
        * time_weight
    )

    return round(score, 2)
def calculate_daily_workload(total_remaining_minutes, days_left):
    if total_remaining_minutes <= 0:
        return 0

    DEFAULT_DAILY_MINUTES = 120

    return min(
        DEFAULT_DAILY_MINUTES,
        total_remaining_minutes
    )

def allocate_daily_minutes(tasks, daily_target_minutes):
    if not tasks or daily_target_minutes <= 0:
        return []

    selected_tasks = tasks[:3]

    allocations = {
        task["task_id"]: 0
        for task in selected_tasks
    }

    remaining_target = daily_target_minutes

    while remaining_target > 0:
        available_tasks = [
            task for task in selected_tasks
            if allocations[task["task_id"]] < task["remaining_minutes"]
        ]

        if not available_tasks:
            break

        total_score = sum(
            task["score"]
            for task in available_tasks
        )

        if total_score <= 0:
            break

        allocated_this_round = 0

        for task in available_tasks:
            task_id = task["task_id"]

            available_minutes = (
                task["remaining_minutes"]
                - allocations[task_id]
            )

            share = round(
                remaining_target
                * task["score"]
                / total_score
            )

            share = min(
                share,
                available_minutes
            )

            allocations[task_id] += share
            allocated_this_round += share

        if allocated_this_round <= 0:
            break

        remaining_target -= allocated_this_round

    result = []

    for task in selected_tasks:
        result.append({
            "task_id": task["task_id"],
            "title": task["title"],
            "remaining_minutes": task["remaining_minutes"],
            "allocated_minutes": allocations[task["task_id"]],
            "score": task["score"]
        })

    return result
def select_today_tasks(tasks, daily_minutes=120):
    selected = []
    total_minutes = 0

    for task in tasks:
        if total_minutes + task["estimated_minutes"] <= daily_minutes:
            selected.append(task)
            total_minutes += task["estimated_minutes"]

    return selected