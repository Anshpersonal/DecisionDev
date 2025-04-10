
import cx from 'classnames';
import { MachineLearning } from '@carbon/icons-react';
import styles from './ChatBot.module.scss';

export interface ChatMessage {
  id: string,
  name: string,
  message: string,
  direction: 'sent' | 'received',
  type?: 'system' |'text' | 'error'
}

type MessageProps = Omit<ChatMessage, 'id'>;

export default function Message({
  name, message, direction, type = 'text',
}: MessageProps) {
  return (
    <div>
      <div className={styles.messageContainer} style={{ alignItems: direction === 'sent' ? 'end' : 'start' }}>
        <div className={styles.nameWrapper}>
          {direction === 'received' && <MachineLearning className={styles.icon} /> }
          <div className={styles.username}>{name}</div>
        </div>
        {type === 'text' && <div className={cx(styles.message, { [styles.sent]: direction === 'sent' })}>{message}</div>}
        {type === 'error' && <div className={styles.errorMessage}>{message}</div>}
      </div>
    </div>
  );
}
