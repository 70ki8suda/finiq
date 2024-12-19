import Link from 'next/link';
import { getCategories } from '@/lib/markdown';
import styles from './page.module.css';

export default function HomePage() {
  const categories = getCategories();

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>FINIQ</h1>
      <div>
        {categories.map((category) => (
          <Link key={category} href={`/${category}`} className={styles.categoryLink}>
            {category.toUpperCase()}
          </Link>
        ))}
      </div>
    </div>
  );
}
