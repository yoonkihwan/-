import csv
import io

class FormatterService:
    def to_csv(self, text: str, delimiter='	') -> str:
        """입력된 텍스트를 CSV 형식으로 변환합니다. (기본 구분자: 탭)"""
        if not text.strip():
            return ""
        
        output = io.StringIO()
        # 각 줄을 읽어와서 구분자로 분리 후 CSV로 작성
        reader = csv.reader(text.strip().splitlines(), delimiter=delimiter)
        writer = csv.writer(output)
        writer.writerows(reader)
        
        return output.getvalue().strip()

    def to_markdown_table(self, text: str, delimiter='	') -> str:
        """입력된 텍스트를 Markdown 테이블 형식으로 변환합니다."""
        if not text.strip():
            return ""

        lines = text.strip().splitlines()
        reader = list(csv.reader(lines, delimiter=delimiter))
        
        if not reader:
            return ""

        # 헤더와 본문 분리
        header = reader[0]
        body = reader[1:]
        num_cols = len(header)

        # 마크다운 테이블 생성
        md_table = "| " + " | ".join(header) + " |\n"
        md_table += "| " + " | ".join(["---"] * num_cols) + " |\n"
        for row in body:
            # 행의 열 개수가 헤더와 다를 경우 빈 문자열로 채움
            while len(row) < num_cols:
                row.append("")
            md_table += "| " + " | ".join(row[:num_cols]) + " |\n"
            
        return md_table.strip()

    def to_list(self, text: str, prefix="- ") -> str:
        """각 줄의 시작 부분에 지정된 접두사를 붙여 리스트로 만듭니다."""
        if not text.strip():
            return ""
        
        lines = text.strip().splitlines()
        return "\n".join([f"{prefix}{line.strip()}" for line in lines])

    def space_to_newline(self, text: str) -> str:
        """공백을 줄바꿈으로 변환합니다."""
        return text.strip().replace(' ', '\n')