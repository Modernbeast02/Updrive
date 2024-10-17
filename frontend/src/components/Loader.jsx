import React from 'react'
import styles from '../styles/loader.module.css'

const Loader = () => {
  return (
    <>
    <div className={styles.body}>
    <section className={styles.sectionStyle}>
    <div className={styles.dot}></div>
    </section>
    </div>
    </>
  )
}

export default Loader