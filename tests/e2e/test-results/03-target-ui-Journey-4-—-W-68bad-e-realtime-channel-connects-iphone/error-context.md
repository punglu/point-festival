# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - link "몽글 홈" [ref=e5] [cursor=pointer]:
      - /url: /dashboard
      - text: 몽글
    - combobox "활성 가족 선택" [ref=e7]:
      - option "Synthetic Family Alpha" [selected]
      - option "Synthetic Family Beta"
    - button "로그아웃" [ref=e9] [cursor=pointer]
  - main [ref=e11]:
    - region "와글와글" [ref=e12]:
      - generic [ref=e13]:
        - generic [ref=e14]:
          - button "대화방 목록으로" [ref=e15] [cursor=pointer]: ←
          - heading "가족 대화" [level=2] [ref=e16]
          - generic [ref=e17]: 실시간 연결됨
        - list [ref=e18]:
          - listitem [ref=e19]:
            - generic [ref=e20]: hello-1785583696695
          - listitem [ref=e21]:
            - generic [ref=e22]: missed-1785583698850
        - generic [ref=e23]:
          - generic [ref=e24]: 메시지 입력
          - textbox "메시지 입력" [ref=e25]:
            - /placeholder: 메시지를 입력하세요
          - button "보내기" [disabled] [ref=e26]
  - navigation "몽글 모바일 탐색" [ref=e27]:
    - link "마크포인트" [ref=e28] [cursor=pointer]:
      - /url: /dashboard
      - generic [ref=e29]: 마크포인트
    - link "와글와글" [ref=e30] [cursor=pointer]:
      - /url: /wagle
      - generic [ref=e31]: 와글와글
    - link "가족" [ref=e32] [cursor=pointer]:
      - /url: /family
      - generic [ref=e33]: 가족
```