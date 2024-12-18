import { getArticleBySlug, getAllArticles, getCategories } from '@/lib/markdown';
import styles from './page.module.css';

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
    </article>
  );
}
