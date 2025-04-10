
import { unstable__Slug as Slug } from '@carbon/react';
import styles from './ChatBot.module.scss';

export default function Header() {
  return (
    <div className={styles.header}>
      <div className={styles.slug}>
        <Slug
          size="xs"
        />
      </div>
    </div>
  );
}
