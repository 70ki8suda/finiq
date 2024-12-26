import { getArticleBySlug, getAllArticles, getCategories } from '@/lib/markdown';
import styles from './page.module.css';
import Link from 'next/link';
import ArticleCard from '@/app/_components/ArticleCard/ArticleCard';

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

export default async function ArticlePage({ params }: { params: Promise<{ category: string; slug: string }> }) {
  const { category, slug } = await params; // Await the params if it's a promise
  const article = await getArticleBySlug(category, slug);

  // Fetch all articles across all categories
  const allArticles = getAllArticles();
  // Filter articles written on the same day
  const sameDayArticles = allArticles.filter((a) => a.date === article.date && a.slug !== slug);
  return (
    <article className={styles.container}>
      <h1 className={styles.title}>{article.title}</h1>
      <time className={styles.date}>{article.date}</time>
      <div className={styles.content} dangerouslySetInnerHTML={{ __html: article.content }} />

      {/* Links to other articles written on the same day */}
      {sameDayArticles.length > 0 && (
        <div className={styles.sameDayArticles}>
          <h2>関連記事</h2>
          {sameDayArticles.map((sameDayArticle) => (
            <Link
              key={sameDayArticle.slug}
              href={`/${sameDayArticle.category}/${sameDayArticle.slug}`}
              className={styles.articleLink}
            >
              <ArticleCard metadata={sameDayArticle} />
            </Link>
          ))}
        </div>
      )}
      <Link href={`/${category}`} className={styles.backButton}>
        <button>{category}記事一覧に戻る</button>
      </Link>
    </article>
  );
}
