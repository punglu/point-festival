import styles from './MissionCreateFormScreen.module.css';
import type { MissionCreateFormProps } from './types';

export function MissionCreateFormScreen({ model, onCancel, onCreate }: MissionCreateFormProps) {
  return (
    <main className={styles.screen} data-canonical-screen-id="2l" data-canonical-screen-label="미션 만들기 폼" data-canonical-source="wave7-full-authority">
      <aside className={styles.sidebar}><strong>우리 가족</strong><span>관리자 모드</span><nav><b>대시보드</b><b className={styles.active}>미션 관리</b><b>포인트 관리</b><b>사용자 관리</b><b>알림 관리</b></nav></aside>
      <section className={styles.content} aria-label="미션 만들기">
        <header><div><span>미션 관리</span><h1>새 미션 만들기</h1><p>가족에게 전달할 미션을 설정해 보세요.</p></div><button type="button" aria-label="닫기" onClick={onCancel}>×</button></header>
        <div className={styles.columns}>
          <form className={styles.form} onSubmit={(event) => { event.preventDefault(); onCreate?.(); }}>
            <label>미션 제목<input defaultValue={model.title} /></label>
            <label>설명<textarea defaultValue={model.description} /></label>
            <fieldset><legend>미션 유형</legend><div className={styles.pills}><span className={styles.selected}>일상</span><span>학습</span><span>가족 협동</span></div></fieldset>
            <div className={styles.pair}><label>담당 자녀<select defaultValue={model.assignees}><option>{model.assignees}</option></select></label><label>반복 주기<select defaultValue="매일"><option>매일</option></select></label></div>
            <div className={styles.pair}><label>보상 포인트<input defaultValue={`${model.points} P`} /></label><label className={styles.toggle}>인증 사진 필수<i /></label></div>
            <label className={styles.toggle}>보호자 승인 필요<i /></label>
            <div className={styles.actions}><button type="button" onClick={onCancel}>취소</button><button type="submit">미션 만들기</button></div>
          </form>
          <aside className={styles.preview}><span>실시간 미리보기</span><article><i>🧹</i><div><strong>{model.title}</strong><p>{model.description}</p></div><b>+{model.points}P</b></article><p className={styles.note}>서연·민준의 오늘 미션에 바로 추가돼요.</p></aside>
        </div>
      </section>
    </main>
  );
}
