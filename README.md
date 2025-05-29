# DataTableStruct 프로젝트

복잡한 구조의 2차원 표 데이터를 해석하고, 헤더 기반 검색 및 시각화까지 제공하는 Python 기반 클래스입니다.

---

## 📁 프로젝트 구성

```
Project/
│
├── TableClass.py              # DataTableStruct 클래스 정의 파일
├── README.md                  # 프로젝트 설명 문서(md)
├── README.txt                 # 프로젝트 설명 문서(txt)
└── requirements.txt           # 의존 패키지 명세
```

---

## 💻 프로젝트 프로그램 설치방법

1. Python 3.8 이상이 설치되어 있어야 합니다.
2. 프로젝트 루트 폴더에서 다음 명령어 실행:

```bash
pip install -r requirements.txt
```

※ `requirements.txt` 예시:
```
pandas
numpy
```

---

## 🛠 DataTableStruct 클래스: 실제 코드 기반 사용 설명

이 문서는 DataTableStruct 클래스의 함수 사용 방법을 안내합니다.

---

### 1. 클래스 불러오기 및 인스턴스 생성

```python
from TableClass import DataTableStruct
table = DataTableStruct()
```

- TableClass.py에서 DataTableStruct 클래스를 불러옵니다.
- 클래스를 사용할 수 있도록 인스턴스를 생성합니다.

---

### 2. 원본 데이터 작성 및 초기화

```python
data = [
    ["", "", "2023", "2024"],
    ["", "", "Q1", "Q2"],
    ["A", "제품1", 100, 200],
    ["B", "제품2", 150, 250],
]
table.Init(data, rowHeadersNumber=2, columnHeadersNumber=2, use_pure_table=True)
```

- Init() 함수를 통해 사용할 데이터 배열을 구성 요소별로 분리합니다.
- 사용 형식: Init(데이터배열, 행 헤더 열 수, 열 헤더 행 수, 퓨어테이블 모드 사용 여부)
- 퓨어테이블 모드를 사용할 경우, 표가 아래와 같이 구성됩니다:

```
["", "", "", "A", "B"]
["", "", "", "2023", "2024"],
["", "", "", "Q1", "Q2"],
["1", "A", "제품1", 100, 200],
["2", "B", "제품2", 150, 250],
```

---

### 3. 셀 값 검색: SearchData()

```python
table.SearchData("Q1", "A")  # → 100
```

- 지정한 행과 열의 헤더 값을 기준으로 해당 교차 지점의 셀 값을 반환합니다.

---

### 4. 테이블 출력: ShowTable()

```python
df = table.ShowTable()
```

- 앞서 분리한 데이터들을 기반으로 최종 DataFrame 객체를 생성합니다.
- 생성된 df 변수를 출력하면 표 형태로 확인할 수 있습니다.

---

### 전체 흐름 요약:

```
Init() 호출
  └→ 데이터 정리
SearchData()
  └→ 헤더값 매칭하여 셀 위치 탐색
ShowTable()
  └→ 헤더/데이터 결합한 DataFrame 반환
```

---

## 👨‍💻 프로그래머 정보

- **이름**: 고재현 (Jaehyeon Ko)  
  - **이메일**: wogus2562@korea.ac.kr

- **이름**: 김찬혁 (Chanhyuk Kim)  
  - **이메일**: cksgur6070@gmail.com

---

## 🐞 버그 및 디버그

- 버그 리포트는 GitHub Issue 또는 이메일로 접수 부탁드립니다.
- 공지된 주요 디버깅 사항은 여기에 업데이트될 예정입니다.

---

## 🔗 참고 및 출처

- [Pandas 공식문서](https://pandas.pydata.org/)
- [NumPy 공식문서](https://numpy.org/)

---

## 📌 버전 및 업데이트 정보

| 버전  | 날짜        | 변경 내용       |
|--------|-------------|----------------|
| 1.0    | 2025-04-11  | 최초 버전 공개 |
|        |             |                |

---
