export type NotificationItem = {
  icon: string;
  title: string;
  text: string;
  time: string;
  unread: boolean;
};

export type NotificationListModel = {
  unreadCount: number;
  filters: string[];
  activeFilter: string;
  todayLabel: string;
  notifications: NotificationItem[];
  footerNote: string;
};

export type NotificationListProps = {
  model: NotificationListModel;
  onBack?: () => void;
  onMarkAllRead?: () => void;
  onFilter?: (name: string) => void;
  onSelectNotification?: (notification: NotificationItem) => void;
};
