import { getAllArticles, getCategories } from '@/lib/markdown';
import Link from 'next/link';

export async function generateStaticParams() {
  const categories = getCategories();
  return categories.map((category) => ({
    category,
  }));
}

export default async function CategoryPage({ params: { category } }: { params: { category: string } }) {
  const articles = getAllArticles(category);

  return (
    <div>
      <h1>{category.toUpperCase()} Articles</h1>
      <div>
        {articles.map((article) => (
          <article key={article.slug}>
            <Link href={`/${category}/${article.slug}`}>
              <h2>{article.title}</h2>
              <time>{article.date}</time>
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
