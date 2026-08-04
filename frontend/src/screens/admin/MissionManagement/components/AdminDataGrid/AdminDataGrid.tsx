import type { ReactNode } from 'react';
import styles from './AdminDataGrid.module.css';

export type AdminDataGridColumn<T> = {
  key: string;
  header: string;
  align?: 'left' | 'center' | 'right';
  render: (row: T) => ReactNode;
};

export type AdminDataGridProps<T> = {
  rows: T[];
  rowKey: (row: T) => string | number;
  /** Table mode: renders a real <table> with the existing detailTable/
   *  data-label mobile-card convention (see CardDetailTable). */
  columns?: AdminDataGridColumn<T>[];
  /** Card-grid mode: renders each row via an existing, already-real row
   *  component (e.g. MissionCard/MissionCardEdit) inside a responsive
   *  CSS grid -- this mode composes existing components rather than
   *  reimplementing their per-status conditional logic. */
  renderRow?: (row: T) => ReactNode;
  loading?: boolean;
  loadingLabel?: string;
  emptyLabel?: string;
};

/**
 * Admin-local data grid shell. Provides the grid chrome (loading/empty
 * state, responsive table-vs-card layout) for Admin list surfaces.
 * Colocated at AdminDashboard-feature level per the Frontend Development
 * Guide's "local-first, promote only after a second real consumer" rule --
 * not yet promoted to a global shared component.
 */
export function AdminDataGrid<T>({
  rows,
  rowKey,
  columns,
  renderRow,
  loading,
  loadingLabel = '로딩 중...',
  emptyLabel = '데이터가 없습니다',
}: AdminDataGridProps<T>) {
  if (loading) {
    return <p className={styles.loading}>{loadingLabel}</p>;
  }

  if (rows.length === 0) {
    return <div className={styles.empty}>{emptyLabel}</div>;
  }

  if (columns) {
    return (
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} style={{ textAlign: col.align ?? 'left' }}>{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={rowKey(row)}>
                {columns.map((col) => (
                  <td key={col.key} data-label={col.header} style={{ textAlign: col.align ?? 'left' }}>
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className={styles.cardGrid}>
      {rows.map((row) => (
        <div key={rowKey(row)} className={styles.cardGridItem}>
          {renderRow?.(row)}
        </div>
      ))}
    </div>
  );
}
