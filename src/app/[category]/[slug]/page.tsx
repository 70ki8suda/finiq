import { getArticleBySlug, getAllArticles, getCategories } from '@/lib/markdown';
import styles from './page.module.css';
import Link from 'next/link';

export async function generateStaticParams() {
  const categories = getCategories();
  return categories.flatMap((category) => {
    const articles = getAllArticles(category);
    return articles.map((article) => ({
      category,
      slug: article.slug,
    }));
  });
}

export default async function ArticlePage({ params }: { params: { category: string; slug: string } }) {
  const { category, slug } = await params;
  const article = await getArticleBySlug(category, slug);
  return (
    <article className={styles.container}>
      <h1 className={styles.title}>{article.title}</h1>
      <time className={styles.date}>{article.date}</time>
      <div className={styles.content} dangerouslySetInnerHTML={{ __html: article.content }} />
      <Link href={`/${category}`} className={styles.backButton}>
        <button>{category}記事一覧に戻る</button>
      </Link>
    </article>
  );
}
