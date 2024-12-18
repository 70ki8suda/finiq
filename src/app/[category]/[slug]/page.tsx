import { getArticleBySlug, getAllArticles, getCategories } from '@/lib/markdown';

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

export default async function ArticlePage({
  params: { category, slug },
}: {
  params: { category: string; slug: string };
}) {
  const article = await getArticleBySlug(category, slug);

  return (
    <article>
      <h1>{article.title}</h1>
      <time>{article.date}</time>
      <div dangerouslySetInnerHTML={{ __html: article.content }} />
    </article>
  );
}
