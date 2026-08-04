import { ParentDashboardScreen, parentDashboardFixture } from '../../screens/admin/ParentDashboard';

const activityFeed = [
  '서연이가 숙제 다 하기를 완료했어요',
  '민준이가 방 청소를 완료했어요',
  '아빠가 가족 앨범에 사진을 추가했어요',
];

const pendingFeed = ['방 청소하기 · 서연', '동생과 사이좋게 지내기 · 민준', '숙제 다 하기 · 서연'];

export function ParentDashboardPreview() {
  return (
    <ParentDashboardScreen
      model={parentDashboardFixture}
      playerStatusSlot={
        <article>
          <h2>오늘의 가족 활동</h2>
          {activityFeed.map((activity) => <div key={activity}>● {activity}</div>)}
        </article>
      }
      pendingMissionSlot={
        <article>
          <h2>승인 대기</h2>
          {pendingFeed.map((item) => <div key={item}>{item}</div>)}
        </article>
      }
    />
  );
}
