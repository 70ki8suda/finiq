import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

const contentDirectory = path.join(process.cwd(), 'content');

interface ArticleMetadata {
  slug: string;
  category: string;
  date: string;
  title: string;
}

export async function getArticleBySlug(category: string, slug: string) {
  const fullPath = path.join(contentDirectory, category, `${slug}.md`);
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);

  const processedContent = await remark().use(html).process(content);
  const contentHtml = processedContent.toString();

  return {
    slug,
    content: contentHtml,
    category,
    title: data.title,
    date: data.date,
  };
}

export function getAllArticles(category?: string) {
  const categories = category ? [category] : fs.readdirSync(contentDirectory);

  const articles: ArticleMetadata[] = categories.flatMap((cat) => {
    const categoryPath = path.join(contentDirectory, cat);
    const fileNames = fs.readdirSync(categoryPath);

    return fileNames.map((fileName) => {
      const slug = fileName.replace(/\.md$/, '');
      const fullPath = path.join(categoryPath, fileName);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const { data } = matter(fileContents);

      return {
        slug,
        category: cat,
        title: data.title,
        date: data.date,
      };
    });
  });

  return articles.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getCategories() {
  if (!fs.existsSync(contentDirectory)) {
    fs.mkdirSync(contentDirectory);
    return [];
  }
  return fs.readdirSync(contentDirectory);
}
