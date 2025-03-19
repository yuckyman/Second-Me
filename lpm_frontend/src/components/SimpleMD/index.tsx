import classNames from 'classnames';
import { marked } from 'marked';
import markedLinkifyIt from 'marked-linkify-it';
import { type CSSProperties, memo, useEffect, useRef } from 'react';

import styles from './index.module.css';

export interface IProps {
  className?: string;
  style?: CSSProperties;
  children?: React.ReactNode;
  content?: string;
  id?: string;
}

const renderer = new marked.Renderer();

// markdown
marked.setOptions({ renderer });
marked.use(markedLinkifyIt());

function SimplyMD(props: IProps) {
  const { className, content, style } = props;
  const markdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (markdownRef.current) {
      markdownRef.current.innerHTML = marked.parse(content ?? '');

      markdownRef.current.innerHTML = markdownRef.current.innerHTML
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>');
    }
  }, [content]);

  return (
    <div className={styles.markdown}>
      <div ref={markdownRef} className={classNames(className, 'relative')} style={style} />
    </div>
  );
}

export default memo(SimplyMD);
