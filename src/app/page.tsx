import Link from 'next/link';
import { getCategories } from '@/lib/markdown';
import { getAllArticles } from '@/lib/markdown';
import styles from './page.module.css';
import ArticleCard from './_components/ArticleCard/ArticleCard';

export default function HomePage() {
  const categories = getCategories();
  const articles = getAllArticles().slice(0, 5);
  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>FINIQ</h1>
      <div className={styles.recentArticles}>
        <h2 className={styles.recentArticles_heading}>新着記事</h2>
        {articles.map((article) => (
          <Link key={article.slug} href={`/${article.category}/${article.slug}`} className={styles.articleLink}>
            <ArticleCard metadata={article} />
          </Link>
        ))}
      </div>
      <div>
        <h2 className={styles.categories_heading}>カテゴリ一覧</h2>
        {categories.map((category) => (
          <Link key={category} href={`/${category}`} className={styles.categoryLink}>
            {category.toUpperCase()}
          </Link>
        ))}
      </div>
    </div>
  );
}
