import styles from './ArticleCard.module.css';

interface ArticleMetadata {
  category: string;
  date: string;
  summary: string;
  tags: string[];
  title: string;
}

const ArticleCard = ({ metadata }: { metadata: ArticleMetadata }) => {
  return (
    <div className={styles.card}>
      <div className={styles.meta}>
        {metadata.category} • {new Date(metadata.date).toLocaleDateString('ja-JP')}
      </div>
      <h2 className={styles.title}>{metadata.title}</h2>
      <p className={styles.summary}>{metadata.summary}</p>
      <div className={styles.tags}>
        {metadata.tags.map((tag) => (
          <span key={tag} className={styles.tag}>
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
};

export default ArticleCard;
