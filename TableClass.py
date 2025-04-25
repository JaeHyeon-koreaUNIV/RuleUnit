import pandas as pd
import numpy as np
import string

class DataTableStruct:
    def __init__(self):
        # 원본 데이터 보관
        self.dataTable = None

        # 분리된 표 구성 요소
        self.corners = None         # 코너: (열헤더 행 수) x (행헤더 열 수)
        self.rowHeaders = None      # 행 헤더: 실제 데이터 행 수 x (행헤더 열 수)
        self.columnHeaders = None   # 열 헤더: (열헤더 행 수) x (데이터 열 수)
        self.rawData = None         # 본문 데이터: 실제 데이터 행 수 x (데이터 열 수)

        # 검색용 MultiIndex 후보 (튜플 형태)
        self.rowHeaders_showTable = None   # 각 행 헤더를 튜플로 변환
        self.columnHeaders_showTable = None  # 각 열 헤더를 튜플로 변환

        # 헤더 깊이
        self.rowHeadersNumb = None      # 행 헤더 열 수 (헤더의 깊이)
        self.columnHeadersNumb = None   # 열 헤더 행 수 (헤더의 깊이)

        # 최종 DataFrame
        self.df = None

        # PureTable 모드 여부
        self.use_pure_table = False

    def Init(self, dataTable, rowHeadersNumber, columnHeadersNumber, use_pure_table=False):
        """
        dataTable (2D 배열)을
         - 좌측 rowHeadersNumber 열 → 행 헤더
         - 상단 columnHeadersNumber 행 → 열 헤더
         - 교차하는 영역 → 코너(corners)
         - 나머지 → 본문(rawData)
        로 분리하고, 검색용 튜플 변환 등 내부 구조를 준비합니다.
        """
        self.dataTable = dataTable
        self.rowHeadersNumb = rowHeadersNumber
        self.columnHeadersNumb = columnHeadersNumber
        self.use_pure_table = use_pure_table

        # 1) 코너 추출 (양쪽 헤더가 있을 때)
        if rowHeadersNumber > 0 and columnHeadersNumber > 0:
            self.corners = [row[:rowHeadersNumber] for row in dataTable[:columnHeadersNumber]]
        else:
            self.corners = None

        # 2) 행 헤더 추출 (코너 영역 제외)
        if rowHeadersNumber > 0:
            self.rowHeaders = [row[:rowHeadersNumber] for row in dataTable[columnHeadersNumber:]]
        else:
            self.rowHeaders = None

        # 3) 열 헤더 추출 (코너 영역 제외)
        if columnHeadersNumber > 0:
            self.columnHeaders = [row[rowHeadersNumber:] for row in dataTable[:columnHeadersNumber]]
        else:
            self.columnHeaders = None

        # 4) 본문 데이터 추출
        self.rawData = [row[rowHeadersNumber:] for row in dataTable[columnHeadersNumber:]]

        # 5) PureTable 모드일 때만 검색용 라벨 생성
        if self.use_pure_table and self.rowHeaders:
            self.rowHeaders_showTable = [tuple(r) for r in self.rowHeaders]
        else:
            self.rowHeaders_showTable = None

        if self.use_pure_table and self.columnHeaders:
            transposed = list(zip(*self.columnHeaders))
            self.columnHeaders_showTable = [tuple(c) for c in transposed]
        else:
            self.columnHeaders_showTable = None

        # 6) PureTable 모드라면, 검색용에 추가 라벨(숫자/알파벳)을 prepend
        if self.use_pure_table:
            self._apply_puretable_labels_for_search()

    def _apply_puretable_labels_for_search(self):
        """
        PureTable 모드에서 검색용 헤더 튜플에 추가 레벨을 prepend하여,
         - 행 헤더는 ('1', ...) 형식
         - 열 헤더는 ('A', ...) 형식
        로 만들어, '1','A' 등의 검색이 가능하도록 한다.
        (표시용 확장은 ShowTable에서 별도 처리)
        """
        # 행 헤더에 숫자 라벨 추가
        if self.rowHeaders_showTable:
            updated = []
            for i, t in enumerate(self.rowHeaders_showTable):
                updated.append((str(i+1),) + t)
            self.rowHeaders_showTable = updated
        else:
            if self.rawData:
                updated = []
                for i in range(len(self.rawData)):
                    updated.append((str(i+1),))
                self.rowHeaders_showTable = updated

        # 열 헤더에 알파벳 라벨 추가
        data_cols = len(self.rawData[0]) if (self.rawData and len(self.rawData)>0) else 0
        if self.columnHeaders_showTable:
            updated = []
            for j, t in enumerate(self.columnHeaders_showTable):
                letter = chr(65+j) if j < 26 else f"Col{j+1}"
                updated.append((letter,) + t)
            self.columnHeaders_showTable = updated
        else:
            if data_cols > 0:
                updated = []
                for j in range(data_cols):
                    letter = chr(65+j) if j < 26 else f"Col{j+1}"
                    updated.append((letter,))
                self.columnHeaders_showTable = updated

    def _get_cell_indices(self, rowCompareData, columnCompareData):
        """
        입력받은 행/열 헤더(또는 라벨) 정보를 통해, rawData 내의 (row, col) 인덱스를 찾아 반환합니다.
        PureTable 모드에서 추가된 라벨('1','A')가 입력되면 이를 무시하고 원본 헤더와 매칭합니다.
        rowCompareData와 columnCompareData는 단일 문자열 또는 튜플로 입력할 수 있으며,
        튜플인 경우 각 요소가 모두 해당 헤더에 포함되어 있는 행(또는 열)을 찾습니다.
        인덱스를 찾지 못하면 (None, None) 또는 각각 None을 반환합니다.
        """
        # 개별 항목을 처리하는 내부 함수 (PureTable 라벨 변환 적용)
        def process_row_item(item):
            if self.use_pure_table and isinstance(item, str) and len(item) == 1 and item.isdigit() and self.rowHeaders_showTable:
                idx = int(item) - 1
                if 0 <= idx < len(self.rowHeaders_showTable):
                    t = self.rowHeaders_showTable[idx]
                    return t[1] if len(t) > 1 else t[0]
            return item

        def process_col_item(item):
            if self.use_pure_table and isinstance(item, str) and len(item) == 1 and item.upper() in string.ascii_uppercase and self.columnHeaders_showTable:
                idx = ord(item.upper()) - ord('A')
                if 0 <= idx < len(self.columnHeaders_showTable):
                    t = self.columnHeaders_showTable[idx]
                    return t[1] if len(t) > 1 else t[0]
            return item

        # rowCompareData와 columnCompareData가 튜플이면 그대로, 아니면 단일 값으로 리스트화
        row_compare_list = [process_row_item(item) for item in (rowCompareData if isinstance(rowCompareData, tuple) else (rowCompareData,))]
        col_compare_list = [process_col_item(item) for item in (columnCompareData if isinstance(columnCompareData, tuple) else (columnCompareData,))]

        row_index = None
        col_index = None

        # rowHeaders에서 모든 비교값이 포함된 행 찾기
        if self.rowHeaders and all(val is not None for val in row_compare_list):
            row_index = next(
                (i for i, hdr in enumerate(self.rowHeaders) if all(comp in hdr for comp in row_compare_list)),
                None
            )
        # columnHeaders는 열 단위(전치된 상태)로 검사
        if self.columnHeaders and all(val is not None for val in col_compare_list):
            col_index = next(
                (j for j, hdr in enumerate(zip(*self.columnHeaders)) if all(comp in hdr for comp in col_compare_list)),
                None
            )

        return row_index, col_index

    def SearchData(self, rowCompareData, columnCompareData):
        """
        입력받은 (행, 열) 헤더(또는 라벨)에 해당하는 rawData의 셀 값을 반환합니다.
        """
        row_idx, col_idx = self._get_cell_indices(rowCompareData, columnCompareData)
        if row_idx is not None and col_idx is not None:
            return self.rawData[row_idx][col_idx]
        return None

    # ────────────── PureTable 모드용 재구성 함수들 ──────────────
    def _build_corners_pure(self):
        """
        PureTable 모드에서 확장된 코너 블록 생성:
         - 원래 코너 영역의 크기: (columnHeadersNumb) x (rowHeadersNumb)
         - 확장 후: (columnHeadersNumb+1) x (rowHeadersNumb+1)
           → 단, PureTable 모드에서는 코너에 추가 라벨(숫자/알파벳)을 넣지 않고,
              맨 윗 행과 맨 왼쪽 열은 빈 문자열("")로 두며,
              나머지 영역에 원본 코너 셀(있으면) 또는 기본값 "--"을 채웁니다.
        """
        N = self.columnHeadersNumb  # 원래 열헤더 행 수
        M = self.rowHeadersNumb     # 원래 행헤더 열 수
        # 확장된 코너 블록: (N+1) x (M+1)
        block = [["" for _ in range(M+1)] for _ in range(N+1)]
        # 나머지 영역에 원래 코너 셀 복사 또는 기본값 채우기
        if self.corners:
            for i in range(N):
                for j in range(M):
                    block[i+1][j+1] = self.corners[i][j]
        else:
            for i in range(N):
                for j in range(M):
                    block[i+1][j+1] = "--"
        return block

    def _build_colHeaders_pure(self):
        """
        PureTable 모드에서 확장된 열 헤더 블록 생성:
         - 원래 열헤더의 크기: (columnHeadersNumb) x (dataCols)
         - 확장 후: (columnHeadersNumb+1) x (dataCols)
           → 첫 행: 알파벳 라벨 (추가 헤더)
           → 이후 행: 원래 열헤더(있으면) 또는 기본값 "--"
        """
        N = self.columnHeadersNumb
        dataCols = len(self.rawData[0]) if (self.rawData and len(self.rawData) > 0) else 0
        block = []
        # 첫 행: 알파벳 라벨
        first_row = []
        for j in range(dataCols):
            first_row.append(chr(65+j) if j < 26 else f"Col{j+1}")
        block.append(first_row)
        # 나머지 N행: 원래 열헤더가 있으면 그대로, 없으면 기본값
        if self.columnHeaders and N > 0:
            for i in range(N):
                block.append(list(self.columnHeaders[i]))
        else:
            for i in range(N):
                block.append(["--"] * dataCols)
        return block

    def _build_rowHeaders_pure(self):
        """
        PureTable 모드에서 확장된 행 헤더 블록 생성:
         - 원래 행헤더의 크기: (dataRows) x (rowHeadersNumb)
         - 확장 후: (dataRows) x (rowHeadersNumb+1)
           → 각 행: 맨 왼쪽 셀은 숫자 라벨, 나머지는 원래 행헤더(있으면) 또는 기본값 "--"
        """
        M = self.rowHeadersNumb
        dataRows = len(self.rawData) if self.rawData else 0
        block = []
        if self.rowHeaders and M > 0:
            for i in range(dataRows):
                row = [str(i+1)] + list(self.rowHeaders[i])
                block.append(row)
        else:
            for i in range(dataRows):
                block.append([str(i+1)])
        return block

    def ShowTable(self):
        """
        최종 DataFrame을 생성하여 반환합니다.
         - PureTable 모드가 False이면 원본 코너, 행헤더, 열헤더, 본문을 그대로 재구성합니다.
         - PureTable 모드가 True이면 확장된 (추가 라벨 포함) 행헤더와 열헤더는 확장되지만,
           코너 부분은 추가 라벨 없이 원본 데이터를 그대로 사용합니다.
        최종 DataFrame의 자동 인덱스/컬럼 라벨은 제거되어, 오직 표 데이터만 표시됩니다.
        """
        if not self.use_pure_table:
            # PureTable 모드 OFF: 원본 재구성
            reconstructed = []
            # 상단: 코너 + 열헤더
            if self.corners and self.columnHeaders:
                for i in range(self.columnHeadersNumb):
                    row_part = self.corners[i] + self.columnHeaders[i]
                    reconstructed.append(row_part)
            elif self.columnHeaders:
                for i in range(self.columnHeadersNumb):
                    reconstructed.append(self.columnHeaders[i])
            elif self.corners:
                for i in range(self.columnHeadersNumb):
                    reconstructed.append(self.corners[i])
            # 하단: 행헤더 + rawData
            if self.rowHeaders:
                for i, data_row in enumerate(self.rawData):
                    row_part = self.rowHeaders[i] + data_row
                    reconstructed.append(row_part)
            else:
                for data_row in self.rawData:
                    reconstructed.append(data_row)
        else:
            # PureTable 모드 ON: 확장된 헤더/코너 생성
            corners_disp = self._build_corners_pure()       # (columnHeadersNumb+1) x (rowHeadersNumb+1) (코너는 추가 라벨 없음)
            colHeaders_disp = self._build_colHeaders_pure()   # (columnHeadersNumb+1) x (dataCols)
            rowHeaders_disp = self._build_rowHeaders_pure()   # (dataRows) x (rowHeadersNumb+1)
            reconstructed = []
            # 상단 부분: 코너_disp와 colHeaders_disp를 가로로 결합 (각 행: 코너_disp 행 + colHeaders_disp 행)
            top_rows = len(colHeaders_disp)
            for i in range(top_rows):
                row_part = corners_disp[i] + colHeaders_disp[i]
                reconstructed.append(row_part)
            # 하단 부분: 각 행: rowHeaders_disp 행 + rawData 행
            for i in range(len(rowHeaders_disp)):
                row_part = rowHeaders_disp[i] + self.rawData[i]
                reconstructed.append(row_part)
        # DataFrame 생성 및 자동 인덱스/컬럼 라벨 제거
        df = pd.DataFrame(reconstructed)
        df.index = ["" for _ in range(len(df))]
        df.columns = ["" for _ in range(len(df.columns))]
        return df

    def StyleTable(self):
        """
        최종 DataFrame에 CSS 스타일(테두리, 가운데 정렬, 상단 헤더와 좌측 헤더 볼드 처리)을 적용하여 반환합니다.
        상단 헤더 영역은 columnHeadersNumb (퓨어테이블 모드이면 +1),
        좌측 헤더 영역은 rowHeadersNumb (퓨어테이블 모드이면 +1) 범위로 지정됩니다.
        """
        self.df = self.ShowTable()

        # 상단 헤더(열 헤더) 영역 결정
        top_header_rows = self.columnHeadersNumb + 1 if self.use_pure_table else self.columnHeadersNumb
        # 좌측 헤더(행 헤더) 영역 결정
        left_header_columns = self.rowHeadersNumb + 1 if self.use_pure_table else self.rowHeadersNumb

        styles = [
            {'selector': 'table',
            'props': [('border-collapse', 'collapse'),
                      ('border', '2px solid black')]},
            {'selector': 'td',
            'props': [('border', '1px solid black'),
                      ('padding', '5px'),
                      ('text-align', 'center')]}
        ]

        # 상단 헤더 영역: 표의 첫 top_header_rows 행의 모든 셀에 볼드 처리
        if top_header_rows > 0:
            styles.append(
                {'selector': f'table > tbody > tr:nth-child(-n+{top_header_rows}) td',
                'props': [('font-weight', 'bold')]}
            )

        # 좌측 헤더 영역: 각 행의 첫 left_header_columns 셀에 볼드 처리
        if left_header_columns > 0:
            styles.append(
                {'selector': f'table > tbody > tr td:nth-child(-n+{left_header_columns})',
                'props': [('font-weight', 'bold')]}
            )

        # 숫자형 데이터에 대해 불필요한 뒤 0이 붙지 않도록 'g' 포맷을 적용하는 함수
        def format_number(value):
            if isinstance(value, (float, int)):
                return format(value, 'g')
            return value

        styled = (
            self.df
                .style
                .format(format_number)         # 각 셀의 값이 숫자면 '{:g}' 형식으로 출력
                .set_table_styles(styles)
        )
        return styled
