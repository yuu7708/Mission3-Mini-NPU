
import json
import math
import re
import time

EPSILON = 1e-9
REPEAT_COUNT = 1000


def input_matrix(size, title):
    """사용자로부터 size x size 숫자 배열 입력"""
    while True:
        print(f"\n[{title}]")
        matrix = []

        for row in range(size):
            while True:
                values = input(
                    f"{row + 1}번째 줄 ({size}개 숫자): "
                ).split()

                if len(values) != size:
                    print(f"각 줄에 숫자 {size}개를 입력하세요.")
                    continue

                try:
                    numbers = [float(value) for value in values]

                    if not all(math.isfinite(v) for v in numbers):
                        print("유효한 숫자를 입력하세요.")
                        continue

                    matrix.append(numbers)
                    break

                except ValueError:
                    print("숫자만 입력할 수 있습니다. 다시 입력하세요.")

        return matrix


def valid_matrix(matrix, size):
    """배열의 크기와 숫자 형식 확인"""
    if not isinstance(matrix, list) or len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            return False

        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
            if not math.isfinite(value):
                return False

    return True



def mac_operation(pattern, filter_matrix):
    """MAC: 같은 위치의 값을 곱한 뒤 누적 합산"""
    total = 0.0

    for row in range(len(pattern)):
        for col in range(len(pattern[row])):
            total += pattern[row][col] * filter_matrix[row][col]

    return float(total)



def judge(score_cross, score_x):
    """epsilon을 적용한 Cross/X 판정"""
    if abs(score_cross - score_x) < EPSILON:
        return "UNDECIDED"

    if score_cross > score_x:
        return "Cross"

    return "X"


def normalize_label(label):
    """정답 라벨을 Cross 또는 X로 통일"""
    if not isinstance(label, str):
        return None

    value = label.strip().lower()

    if value in ("+", "cross"):
        return "Cross"

    if value in ("x",):
        return "X"

    return None

def normalize_filter_keys(filter_set):
    """필터 이름을 Cross와 X로 통일"""
    if not isinstance(filter_set, dict):
        return None

    normalized = {}

    for key, value in filter_set.items():
        label = normalize_label(key)

        if label is None:
            continue

        if label in normalized:
            return None

        normalized[label] = value

    if "Cross" not in normalized or "X" not in normalized:
        return None

    return normalized

def measure_time(pattern, filter_matrix):
    """MAC 연산 평균 시간(ms) 측정"""
    start = time.perf_counter()

    for _ in range(REPEAT_COUNT):
        mac_operation(pattern, filter_matrix)

    end = time.perf_counter()

    return (end - start) / REPEAT_COUNT * 1000


def performance_test():
    """3, 5, 13, 25 크기별 연산 성능 측정"""
    print("\n========== 성능 측정 ==========")
    print(f"{'크기':<10}{'평균 시간(ms)':<20}{'연산 횟수':<15}")
    print("-" * 45)

    for size in (3, 5, 13, 25):
        pattern = [
            [1.0 for _ in range(size)]
            for _ in range(size)
        ]

        filter_matrix = [
            [0.5 for _ in range(size)]
            for _ in range(size)
        ]

        average = measure_time(pattern, filter_matrix)
        operations = size * size

        print(
            f"{size} x {size:<5}"
            f"{average:<20.6f}"
            f"{operations:<15}"
        )


def print_matrix(matrix):
    for row in matrix:
        print(" ".join(f"{value:g}" for value in row))


def user_mode():
    """사용자 입력 모드"""
    print("\n========== 필터 입력 ==========")

    filter_a = input_matrix(3, "필터 A 입력")
    filter_b = input_matrix(3, "필터 B 입력")

    while True:
        print("\n[입력한 필터 확인]")
        print("필터 A:")
        print_matrix(filter_a)

        print("\n필터 B:")
        print_matrix(filter_b)

        confirm = input("\n이 필터를 사용하시겠습니까? (y/n): ").strip().lower()

        if confirm == "y":
            break

        if confirm == "n":
            print("필터를 다시 입력합니다.")
            filter_a = input_matrix(3, "필터 A 입력")
            filter_b = input_matrix(3, "필터 B 입력")
        else:
            print("y 또는 n을 입력하세요.")

    pattern = input_matrix(3, "패턴 입력")

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    result = judge(score_a, score_b)

    time_a = measure_time(pattern, filter_a)
    time_b = measure_time(pattern, filter_b)

    print("\n========== MAC 결과 ==========")
    print(f"A 점수: {score_a:.10f}")
    print(f"B 점수: {score_b:.10f}")
    print(f"A 평균 연산 시간: {time_a:.6f} ms")
    print(f"B 평균 연산 시간: {time_b:.6f} ms")

    if result == "UNDECIDED":
        print("UNDECIDED")
    elif result == "Cross":
        print("A")
    else:
        print("B")

    print(f"3 x 3 연산 횟수: {3 * 3}")

    performance_test()


def json_mode():
    """JSON 파일의 패턴을 자동으로 분석"""
    print("\n========== JSON 데이터 분석 ==========")

    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        print("data.json 파일을 찾을 수 없습니다.")
        return

    except json.JSONDecodeError as error:
        print(f"JSON 파일 형식 오류: {error}")
        return

    if not isinstance(data, dict):
        print("JSON 최상위 구조가 올바르지 않습니다.")
        return

    filters = data.get("filters")
    patterns = data.get("patterns")

    if not isinstance(filters, dict) or not isinstance(patterns, dict):
        print("filters 또는 patterns 항목이 올바르지 않습니다.")
        return

    total = 0
    passed = 0
    failed = 0
    failure_reasons = []

    for case_id, case_data in patterns.items():
        total += 1
        reason = None

        print(f"\n[{case_id}]")

        try:
            match = re.fullmatch(r"size_(\d+)_(\d+)", case_id)

            if not match:
                raise ValueError("패턴 이름 형식 오류")

            size = int(match.group(1))

            if size not in (5, 13, 25):
                raise ValueError(f"지원하지 않는 패턴 크기입니다: {size}x{size}")
            filter_key = f"size_{size}"

            if filter_key not in filters:
                raise ValueError(f"{size}x{size} 필터가 없습니다.")

            if not isinstance(case_data, dict):
                raise ValueError("패턴 데이터 구조 오류")

            pattern = case_data.get("input")
            expected = normalize_label(case_data.get("expected"))

            if expected is None:
                raise ValueError("정답 라벨이 올바르지 않습니다.")

            if not valid_matrix(pattern, size):
                raise ValueError(
                    f"패턴 배열 크기가 {size}x{size}와 일치하지 않습니다."
                )

            filter_set = normalize_filter_keys(filters[filter_key])

            if filter_set is None:
                raise ValueError("Cross 또는 X 필터가 없거나 이름이 중복되었습니다.")

            cross_filter = filter_set["Cross"]
            x_filter = filter_set["X"]

            if not valid_matrix(cross_filter, size):
                raise ValueError("Cross 필터 크기 또는 숫자 형식 오류")

            if not valid_matrix(x_filter, size):
                raise ValueError("X 필터 크기 또는 숫자 형식 오류")

            score_cross = mac_operation(pattern, cross_filter)
            score_x = mac_operation(pattern, x_filter)

            result = judge(score_cross, score_x)

            print(f"Cross 점수: {score_cross:.10f}")
            print(f"X 점수: {score_x:.10f}")
            print(f"예상 정답: {expected}")
            print(f"판정 결과: {result}")

            if result == expected:
                passed += 1
                print("결과: PASS")
            else:
                failed += 1
                reason = (
                    f"예상 정답은 {expected}, 실제 판정은 {result}"
                )
                print(f"결과: FAIL - {reason}")

        except (ValueError, TypeError, KeyError, IndexError) as error:
            failed += 1
            reason = str(error)
            print(f"결과: FAIL - {reason}")

        except Exception as error:
            failed += 1
            reason = f"예상하지 못한 오류: {error}"
            print(f"결과: FAIL - {reason}")

        if reason:
            failure_reasons.append((case_id, reason))

    print("\n========== 테스트 요약 ==========")
    print(f"전체 테스트: {total}")
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")

    if failure_reasons:
        print("\n[실패한 테스트와 원인]")
        for case_id, reason in failure_reasons:
            print(f"- {case_id}: {reason}")
    else:
        print("\n실패한 테스트가 없습니다.")

    performance_test()


def main():
    print("================================")
    print("       Mini NPU Simulator")
    print("================================")

    while True:
        print("\n1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("3. 종료")

        choice = input("\n모드를 선택하세요: ").strip()

        if choice == "1":
            user_mode()
        elif choice == "2":
            json_mode()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 1, 2, 3 중에서 입력하세요.")


if __name__ == "__main__":
    main()
