# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - link "몽글 홈" [ref=e5] [cursor=pointer]:
      - /url: /dashboard
      - text: 몽글
    - generic [ref=e6]:
      - generic [ref=e7]: 가족
      - combobox "활성 가족 선택" [ref=e8]:
        - option "가족 선택" [disabled] [selected]
        - option "Synthetic Family Alpha"
        - option "Synthetic Family Beta"
    - generic [ref=e9]:
      - generic [ref=e10]: Synthetic Owner A
      - button "로그아웃" [ref=e11] [cursor=pointer]
  - generic [ref=e12]:
    - navigation "몽글 서비스 탐색" [ref=e13]
    - main [ref=e14]:
      - alert [ref=e15]:
        - generic [ref=e16]:
          - strong [ref=e17]: 가족을 선택해주세요
          - paragraph [ref=e18]: 이 계정에 연결된 가족 중 하나를 선택하면 서비스와 권한을 불러옵니다.
      - heading "가족을 선택해주세요" [level=1] [ref=e20]
```