import { getAllArticles, getCategories } from '@/lib/markdown';
import Link from 'next/link';
import ArticleCard from './_components/ArticleCard/ArticleCard';
import styles from './page.module.css';

export async function generateStaticParams() {
  const categories = getCategories();
  return categories.map((category) => ({
    category,
  }));
}

export default async function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  // paramsを非同期で解決
  const { category } = await params;
  const articles = getAllArticles(category);

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>{category.toUpperCase()} Articles</h1>
      <div className={styles.articles}>
        {articles.map((article) => (
          <Link key={article.slug} href={`/${category}/${article.slug}`} className={styles.articleLink}>
            <ArticleCard
              metadata={{
                ...article,
                tags: article.tags || [],
              }}
            />
          </Link>
        ))}
      </div>
      <Link href='/' className={styles.backButton}>
        <button>Topに戻る</button>
      </Link>
    </div>
  );
}
